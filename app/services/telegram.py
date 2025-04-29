import logging
from telegram.ext import ApplicationBuilder
from app.config import get_settings

logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._app = None

    @property
    def app(self) -> ApplicationBuilder:
        """Lazy load the Telegram application."""
        if self._app is None:
            self._app = (
                ApplicationBuilder()
                .token(self.settings.TELEGRAM_BOT_TOKEN)
                .post_init(self.on_startup)
                .build()
            )
        return self._app

    async def on_startup(self, _) -> None:
        logger.info("Telegram bot initialized")

    async def start(self) -> None:
        """Start the Telegram bot."""
        if self._app is None:
            raise ValueError("Telegram application is not initialized.")
        await self._app.initialize()
        await self._app.start_polling()
        logger.info("Telegram bot started.")

    async def stop(self) -> None:
        """Stop the Telegram bot."""
        if self._app is None:
            raise ValueError("Telegram application is not initialized.")
        await self._app.stop()
        await self._app.shutdown()
        logger.info("Telegram bot stopped.")
