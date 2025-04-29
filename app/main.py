from telegram.ext import (
    CommandHandler,
    filters,
    MessageHandler,
)

from app.utils.logging import setup_logget, get_logger

from app.services.telegram import TelegramService
from app.handlers.telegram.commands import test
from app.handlers.telegram_media_handler import TelegramMediaHandler


def main() -> None:
    # Настройка логирования
    setup_logget(
        "logs/app.log",
        "DEBUG",
        libs=["httpx", "asyncio", "telegram", "discord"],
    )

    logger = get_logger(__name__)

    logger.info("Starting bot...")
    telegram_service = TelegramService()
    application = telegram_service.app

    application.add_handler(CommandHandler("test", test.test))

    # Инициализация обработчика медиа
    media_handler = TelegramMediaHandler()

    # следить только за постами на канале
    application.add_handler(
        MessageHandler(filters.ChatType.CHANNEL, media_handler.handle_message)
    )

    application.run_polling()


if __name__ == "__main__":
    main()
