import json
from pydantic import Field, DirectoryPath, BaseModel
from pydantic_settings import BaseSettings
from typing import Optional, List
from pathlib import Path


class WebhookConfig(BaseModel):
    """Конфигурация вебхука Discord"""

    url: str = Field(..., description="Webhook URL")
    silent: bool = Field(False, description="Silent mode")


class Settings(BaseModel):
    """
    Настройки приложения
    """

    TELEGRAM_BOT_TOKEN: str = Field(
        ..., alias="telegram_bot_token", description="Telegram bot token"
    )
    TEMP_PATH: DirectoryPath = Field(
        Path("temp"), alias="temp_path", description="Path to temporary files"
    )
    DISCORD_WEBHOOKS: List[WebhookConfig] = Field(
        ..., alias="discord_webhooks", description="Discord webhooks"
    )
    DISCORD_MAX_FILE_SIZE: int = Field(
        ..., alias="discord_max_file_size", description="Max file size for discord"
    )
    TELEGRAM_MAX_FILE_SIZE: int = Field(
        ...,
        alias="telegram_max_file_size",
        description="Max file size for Telegram",
    )

    class Config:
        settings_file = "settings.json"
        settings_file_encoding = "utf-8"
        case_sensitive = False
        populate_by_name = True


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Фабрика настроек для ленивой инициализации

    Returns:
        Settings: Экземпляр настроек
    """
    global _settings
    if not _settings:
        config_path = Path(Settings.Config.settings_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Settings file {config_path} not found.")

        data = json.loads(
            config_path.read_text(encoding=Settings.Config.settings_file_encoding)
        )
        _settings = Settings(**data)
        _settings.TEMP_PATH.mkdir(parents=True, exist_ok=True)
    return _settings
