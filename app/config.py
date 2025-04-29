from pydantic import Field, DirectoryPath
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """
    Настройки приложения
    """

    TELEGRAM_BOT_TOKEN: str = Field(..., env="TELEGRAM_TOKEN")
    TEMP_PATH: Path = Field(
        default=Path("temp"), description="Path to temporary files", env="TEMP_PATH"
    )
    DISCORD_WEBHOOK_URL: str = Field(..., env="DISCORD_WEBHOOK_URL")
    DISCORD_USERNAME: str = Field(
        default="TTD Bot",
        description="Username for Discord webhook",
        env="DISCORD_USERNAME",
    )
    DISCORD_MAX_FILE_SIZE: int = Field(
        ..., description="Max file size for discord", env="DISCORD_MAX_FILE_SIZE"
    )
    TELEGRAM_MAX_FILE_SIZE: int = Field(
        default=20 * 1024 * 1024,
        description="Max file size for Telegram",
        env="TELEGRAM_MAX_FILE_SIZE",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Фабрика настроек для ленивой инициализации

    Returns:
        Settings: Экземпляр настроек
    """
    global _settings
    if not _settings:
        _settings = Settings()
        _settings.TEMP_PATH.mkdir(parents=True, exist_ok=True)
    return _settings


_settings: Optional[Settings] = None
