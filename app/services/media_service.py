import io
from pathlib import Path
from typing import List, Optional
from telegram import Message, MessageEntity
from telegram.ext import ContextTypes

from app.models.file_payload import FilePayload
from app.utils.file_utils import download_media
from app.utils.video_converter import convert_mp4_to_gif
from app.utils.logging import get_logger


class MediaService:
    def __init__(self):
        self.logger = get_logger(__name__)

    async def build_payloads(
        self, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> List[FilePayload]:
        payloads: List[FilePayload] = []

        # Обработка фото
        if message.photo:
            self.logger.info("Photo found")
            file_id = message.photo[-1].file_id
            data = await download_media(file_id, context.bot)
            payloads.append(self._make_payload(data, "jpg"))

        # Обработка видео
        if message.video:
            self.logger.info("Video found")
            file_id = message.video.file_id
            data = await download_media(file_id, context.bot)
            payloads.append(self._make_payload(data, "mp4"))

        # Обработка анимации
        if message.animation:
            self.logger.info("Animation found")
            file_id = message.animation.file_id
            data = await download_media(file_id, context.bot)
            gif_data = await convert_mp4_to_gif(data)
            payloads.append(self._make_payload(gif_data, "gif"))

        # TODO: Обработка стикеров

        return payloads

    def _make_payload(self, data: bytes, ext: str) -> FilePayload:
        filename = f"media_{id(data)}.{ext}"
        return FilePayload(data=data, filename=filename)
