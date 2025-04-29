from discord import File, SyncWebhook
from discord.errors import HTTPException
from app.config import get_settings

from app.utils.logging import get_logger


logger = get_logger(__name__)


class DiscordService:
    """
    Класс для работы с Discord
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.webhook = SyncWebhook.from_url(self.settings.DISCORD_WEBHOOK_URL)

    async def send(self, content: str, files: list[File]) -> None:
        """Отправляет сообщение в Discord

        Args:
            content (str): Текст сообщения
            files (list[File]): Список файлов для отправки

        Raises:
            HTTPException: Ошибка при отправке сообщения в Discord
            Exception: Любая другая ошибка
        """

        try:
            if content or files:
                logger.info(f"Sending message to Discord")
                self.webhook.send(
                    content=content,
                    username=self.settings.DISCORD_USERNAME,
                    files=files,
                    wait=True,
                )
                logger.info("Message sent to Discord")

        except Exception as e:
            logger.error(f"Error sending message to Discord: {e}")
            raise e
        except HTTPException as e:
            if e.statis == 413:
                logger.error(
                    "File too large to send. Please reduce the file size and try again."
                )
