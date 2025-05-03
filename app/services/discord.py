from io import BytesIO
from typing import List, Optional

from discord import File as DiscordFile, SyncWebhook
from discord.errors import HTTPException

from app.config import get_settings
from app.utils.logging import get_logger
from app.models.file_payload import FilePayload


class DiscordService:
    """
    Класс для работы с Discord
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.logger = get_logger(__name__)
        self._hooks = [
            (SyncWebhook.from_url(hook.url), hook.silent)
            for hook in self.settings.discord.webhooks
        ]

    async def send(self, content: str = "", payloads: List[FilePayload] = None) -> None:
        """Отправляет сообщение в Discord

        Args:
            content (str): Текст сообщения
            payloads (List[FilePayload]): Список файлов для отправки

        Raises:
            Exception: Любая ошибка
        """

        if not content and not payloads:
            self.logger.warning("No content or files to send to Discord")
            return

        for webhook, silent in self._hooks:
            files: List[DiscordFile] = []
            for file_payload in payloads or []:
                size = len(file_payload.data)
                if size > self.settings.discord.max_file_size:
                    self.logger.warning(
                        f"File {file_payload.filename} is too large: {size} bytes."
                    )
                    continue

                stream = BytesIO(file_payload.data)
                files.append(
                    DiscordFile(
                        fp=stream,
                        filename=file_payload.filename,
                    )
                )

            if not content and not files:
                continue

            try:
                self.logger.info(f"Sending message to Discord webhook: {webhook.url}")
                webhook.send(
                    content=content,
                    files=files or [],
                    wait=True,
                    suppress_embeds=True,
                    silent=silent,
                )
                self.logger.info(f"Message sent to Discord webhook: {webhook.url}")
            except Exception as e:
                self.logger.error(
                    f"Error sending message to Discord webhook: {webhook.url}"
                )
                raise
