FROM python:3.13-slim

WORKDIR /app

# 1. uv 설치 (호스트에서 미리 다운받은 Linux 바이너리 복사)
COPY ai_worker/uv /usr/local/bin/uv
RUN chmod +x /usr/local/bin/uv

# 2. 의존성 패키지 관리 파일을 컨테이너 내부에 복사합니다.
COPY pyproject.toml uv.lock ./

# 3. pyproject.toml에 명시된 의존성 패키지 중에서 'app' 그룹만 설치합니다.
ENV UV_INSECURE_HOST="download.pytorch.org pypi.org files.pythonhosted.org"
RUN uv sync --group ai --no-dev --frozen

# 4. 로컬 소스 코드를 컨테이너 내부로 복사합니다.
COPY ./ai_worker ./ai_worker

# 5. AI 워커 실행
CMD ["uv", "run", "python", "-m", "ai_worker.main"]
