import json
from pydantic import Field, BaseModel
from typing import Optional, List
from pathlib import Path


class TelegramConfig(BaseModel):
    """Конфигурация Telegram бота"""

    admin_ids: List[int] = Field(..., description="Admin IDs")
    bot_token: str = Field(..., description="Telegram bot token")
    max_file_size: int = Field(..., description="Max file size for Telegram")


class WebhookConfig(BaseModel):
    """Конфигурация вебхука Discord"""

    name: str = Field(..., description="Webhook name")
    url: str = Field(..., description="Webhook URL")
    silent: bool = Field(False, description="Silent mode")


class DiscordMessageConfig(BaseModel):
    """Конфигурация сообщения Discord"""

    forward_postfix: str = Field(
        "Repost from Telegram: ", description="Postfix for reposted messages"
    )


class DiscordConfig(BaseModel):
    """Конфигурация Discord"""

    webhooks: List[WebhookConfig] = Field(..., description="Discord webhooks")
    max_file_size: int = Field(..., description="Max file size for Discord")
    message: DiscordMessageConfig = Field(
        ..., description="Discord message configuration"
    )


class GeneralConfig(BaseModel):
    temp_dir: Path = Field(Path("temp"), description="Path to temporary files")


class Settings(BaseModel):
    """Конфигурация приложения"""

    telegram: TelegramConfig
    discord: DiscordConfig
    general: GeneralConfig


# Глобальная переменная для хранения настроек
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Фабрика настроек для ленивой инициализации

    Returns:
        Settings: Экземпляр настроек
    """
    global _settings
    if not _settings:
        config_path = Path("settings.json")
        if not config_path.exists():
            raise FileNotFoundError(f"Settings file {config_path} not found.")

        try:
            raw = config_path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in settings file: {e}") from e

        _settings = Settings(**data)
        _settings.general.temp_dir.mkdir(parents=True, exist_ok=True)
    return _settings
