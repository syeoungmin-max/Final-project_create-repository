from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `health_profiles` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `primary_conditions` JSON NOT NULL,
    `allergies` JSON NOT NULL,
    `current_medications` JSON NOT NULL,
    `lifestyle_exercise` VARCHAR(9) NOT NULL COMMENT 'REGULAR: REGULAR\nIRREGULAR: IRREGULAR\nNONE: NONE' DEFAULT 'NONE',
    `lifestyle_smoking` BOOL NOT NULL DEFAULT 0,
    `lifestyle_alcohol` VARCHAR(8) NOT NULL COMMENT 'NONE: NONE\nMODERATE: MODERATE\nHEAVY: HEAVY' DEFAULT 'NONE',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `user_id` BIGINT NOT NULL,
    CONSTRAINT `fk_health_p_users_35ba10a2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `health_profile_histories` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `snapshot` JSON NOT NULL,
    `changed_by` VARCHAR(6) NOT NULL COMMENT 'USER: USER\nSYSTEM: SYSTEM\nADMIN: ADMIN',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `health_profile_id` BIGINT NOT NULL,
    CONSTRAINT `fk_health_p_health_p_2ba992b0` FOREIGN KEY (`health_profile_id`) REFERENCES `health_profiles` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `medical_documents` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `document_type` VARCHAR(16) NOT NULL COMMENT 'PRESCRIPTION: PRESCRIPTION\nMEDICINE_LABEL: MEDICINE_LABEL\nDISCHARGE_NOTICE: DISCHARGE_NOTICE\nHEALTH_CHECK: HEALTH_CHECK',
    `file_path` VARCHAR(512) NOT NULL,
    `file_format` VARCHAR(3) NOT NULL COMMENT 'PNG: PNG\nJPG: JPG\nPDF: PDF',
    `file_size` INT NOT NULL,
    `upload_status` VARCHAR(10) NOT NULL COMMENT 'PENDING: PENDING\nPROCESSING: PROCESSING\nSUCCESS: SUCCESS\nFAILED: FAILED' DEFAULT 'PENDING',
    `confidence_score` DOUBLE,
    `is_verified` BOOL NOT NULL DEFAULT 0,
    `processed_at` DATETIME(6),
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `user_id` BIGINT NOT NULL,
    CONSTRAINT `fk_medical__users_9d9be28d` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `ocr_results` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `extracted_text` LONGTEXT NOT NULL,
    `structured_data` JSON NOT NULL,
    `important_fields` JSON NOT NULL,
    `masked_pii` BOOL NOT NULL DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `document_id` BIGINT NOT NULL,
    CONSTRAINT `fk_ocr_resu_medical__0805787c` FOREIGN KEY (`document_id`) REFERENCES `medical_documents` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `medications` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `medication_name` VARCHAR(200) NOT NULL,
    `dosage` VARCHAR(100) NOT NULL,
    `frequency` VARCHAR(100) NOT NULL,
    `duration` VARCHAR(100) NOT NULL,
    `start_date` DATE,
    `end_date` DATE,
    `side_effects` LONGTEXT,
    `precautions` LONGTEXT,
    `interaction_warnings` LONGTEXT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `document_id` BIGINT,
    `user_id` BIGINT NOT NULL,
    CONSTRAINT `fk_medicati_medical__605f55a9` FOREIGN KEY (`document_id`) REFERENCES `medical_documents` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_medicati_users_5f6773a0` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `health_guidances` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `guidance_type` VARCHAR(16) NOT NULL COMMENT 'MEDICATION_GUIDE: MEDICATION_GUIDE\nLIFESTYLE_GUIDE: LIFESTYLE_GUIDE\nDIETARY_GUIDE: DIETARY_GUIDE',
    `content` LONGTEXT NOT NULL,
    `ai_confidence` DOUBLE,
    `requires_expert_review` BOOL NOT NULL DEFAULT 0,
    `verification_status` VARCHAR(8) NOT NULL COMMENT 'PENDING: PENDING\nVERIFIED: VERIFIED\nFLAGGED: FLAGGED' DEFAULT 'PENDING',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `health_profile_id` BIGINT,
    `user_id` BIGINT NOT NULL,
    CONSTRAINT `fk_health_g_health_p_44cd1136` FOREIGN KEY (`health_profile_id`) REFERENCES `health_profiles` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_health_g_users_ee625cc3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
        ALTER TABLE `users` ADD `kakao_id` VARCHAR(50) UNIQUE;
        ALTER TABLE `users` MODIFY COLUMN `birthday` DATE;
        ALTER TABLE `users` MODIFY COLUMN `phone_number` VARCHAR(11);
        ALTER TABLE `users` MODIFY COLUMN `gender` VARCHAR(6) COMMENT 'MALE: MALE\nFEMALE: FEMALE';
        ALTER TABLE `users` MODIFY COLUMN `hashed_password` VARCHAR(128);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` DROP INDEX `kakao_id`;
        ALTER TABLE `users` DROP COLUMN `kakao_id`;
        ALTER TABLE `users` MODIFY COLUMN `birthday` DATE NOT NULL;
        ALTER TABLE `users` MODIFY COLUMN `phone_number` VARCHAR(11) NOT NULL;
        ALTER TABLE `users` MODIFY COLUMN `gender` VARCHAR(6) NOT NULL COMMENT 'MALE: MALE\nFEMALE: FEMALE';
        ALTER TABLE `users` MODIFY COLUMN `hashed_password` VARCHAR(128) NOT NULL;
        DROP TABLE IF EXISTS `medications`;
        DROP TABLE IF EXISTS `health_profile_histories`;
        DROP TABLE IF EXISTS `health_guidances`;
        DROP TABLE IF EXISTS `health_profiles`;
        DROP TABLE IF EXISTS `medical_documents`;
        DROP TABLE IF EXISTS `ocr_results`;"""


MODELS_STATE = (
    "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"
    "/B8jx2mg"
)
