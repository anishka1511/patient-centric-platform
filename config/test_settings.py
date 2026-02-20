from config.settings import settings
from config.logging_config import logger

if __name__ == "__main__":
    logger.info("Testing configuration...")
    logger.info(f"App Name: {settings.app_name}")
    logger.info(f"App Version: {settings.app_version}")
    logger.info(f"OpenAI Model: {settings.openai_model}")
    logger.info(f"Database URL: {settings.database_url}")
    logger.info(f"Allowed Origins: {settings.allowed_origins_list}")
    logger.info("Configuration loaded successfully!")
