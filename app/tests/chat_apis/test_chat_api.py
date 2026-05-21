from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient
from starlette import status
from tortoise.contrib.test import TestCase

from app.main import app

TEST_USER = {
    "email": "chattest@example.com",
    "password": "Password123!",
    "name": "챗봇테스터",
    "gender": "MALE",
    "birth_date": "1995-01-01",
    "phone_number": "01099998888",
}


async def _get_auth_headers(client: AsyncClient) -> dict:
    await client.post("/api/v1/auth/signup", json=TEST_USER)
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": TEST_USER["email"], "password": TEST_USER["password"]},
    )
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


class TestChatSessionAPI(TestCase):
    async def test_create_session_success(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = await _get_auth_headers(client)
            response = await client.post("/api/v1/chat/sessions", json={"title": "두통 상담"}, headers=headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "두통 상담"
        assert "id" in data

    async def test_create_session_unauthorized(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/chat/sessions", json={"title": "두통 상담"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_sessions_success(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = await _get_auth_headers(client)
            await client.post("/api/v1/chat/sessions", json={"title": "세션1"}, headers=headers)
            await client.post("/api/v1/chat/sessions", json={"title": "세션2"}, headers=headers)
            response = await client.get("/api/v1/chat/sessions", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2

    async def test_get_session_detail_not_found(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = await _get_auth_headers(client)
            response = await client.get("/api/v1/chat/sessions/99999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_send_message_success(self):
        mock_answer = "두통의 원인은 다양합니다."
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = await _get_auth_headers(client)
            create_resp = await client.post("/api/v1/chat/sessions", json={"title": "테스트 상담"}, headers=headers)
            session_id = create_resp.json()["id"]

            with patch("app.services.chats.aioredis.from_url") as mock_redis_factory:
                mock_redis = AsyncMock()
                mock_redis.lpush = AsyncMock()
                mock_redis.blpop = AsyncMock(return_value=("key", f'{{"task_id": "abc", "answer": "{mock_answer}"}}'))
                mock_redis.aclose = AsyncMock()
                mock_redis_factory.return_value = mock_redis

                response = await client.post(
                    f"/api/v1/chat/sessions/{session_id}/messages",
                    json={"content": "두통이 있어요"},
                    headers=headers,
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"] == "ASSISTANT"
        assert data["content"] == mock_answer

    async def test_delete_session_success(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = await _get_auth_headers(client)
            create_resp = await client.post("/api/v1/chat/sessions", json={"title": "삭제할 세션"}, headers=headers)
            session_id = create_resp.json()["id"]

            delete_resp = await client.delete(f"/api/v1/chat/sessions/{session_id}", headers=headers)
            assert delete_resp.status_code == status.HTTP_204_NO_CONTENT

            get_resp = await client.get(f"/api/v1/chat/sessions/{session_id}", headers=headers)
            assert get_resp.status_code == status.HTTP_404_NOT_FOUND
