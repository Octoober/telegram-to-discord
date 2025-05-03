from telegram.ext import (
    CommandHandler,
    filters,
    MessageHandler,
)
import os


from app.services.telegram import TelegramService
from app.handlers.telegram.commands import test
from app.handlers.telegram_media_handler import TelegramMediaHandler

from app.utils.logging import setup_logget, get_logger
from app.services.media_service import MediaService
from app.services.discord import DiscordService
from app.config import get_settings


def main() -> None:
    # Настройка логирования
    setup_logget(
        "logs/app.log",
        "DEBUG",
        libs=["httpx", "asyncio", "telegram", "discord"],
    )

    logger = get_logger(__name__)

    logger.info("Starting bot...")
    logger.info(f"PID: {os.getpid()}")

    telegram_service = TelegramService()
    application = telegram_service.app

    application.add_handler(CommandHandler("test", test.test))

    # Инициализация обработчика медиа
    media_handler = TelegramMediaHandler(
        media_service=MediaService(),
        discord_service=DiscordService(),
        settings=get_settings(),
    )

    # следить только за постами на канале
    application.add_handler(
        MessageHandler(filters.ChatType.CHANNEL, media_handler.handle_message)
    )

    application.run_polling()


if __name__ == "__main__":
    main()
