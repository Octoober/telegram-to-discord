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
        self._hooks = [
            (SyncWebhook.from_url(hook.url), hook.silent)
            for hook in self.settings.DISCORD_WEBHOOKS
        ]

    async def send(self, content: str = "", files: list[File] = None) -> None:
        """Отправляет сообщение в Discord

        Args:
            content (str): Текст сообщения
            files (list[File]): Список файлов для отправки

        Raises:
            HTTPException: Ошибка при отправке сообщения в Discord
            Exception: Любая другая ошибка
        """

        if not content and not files:
            logger.warning("No content or files to send to Discord")
            return

        for webhook, silent in self._hooks:
            try:
                logger.info(f"Sending message to Discord webhook: {webhook.url}")
                webhook.send(
                    content=content,
                    files=files or [],
                    wait=True,
                    suppress_embeds=True,
                    silent=silent,
                )
                logger.info(f"Message sent to Discord webhook: {webhook.url}")
            except Exception as e:
                logger.error(f"Error sending message to Discord webhook: {webhook.url}")
                raise
