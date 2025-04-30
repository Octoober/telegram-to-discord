import io
import asyncio
from collections import defaultdict
from typing import List, Tuple


from telegram import Update, MessageOriginChannel
from telegram.ext import ContextTypes
from discord import File

from app.services.discord import DiscordService
from app.utils.file_utils import download_media
from app.utils.video_converter import convert_mp4_to_gif
from app.utils.logging import get_logger
from app.config import get_settings


logger = get_logger(__name__)


class TelegramMediaHandler:
    def __init__(self):
        self.media_groups = defaultdict(list)
        self.lock = asyncio.Lock()
        self.discord = DiscordService()
        self.settings = get_settings()

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработка сообщения от Telegram

        Args:
            update (Update): Обновление от Telegram
            context (ContextTypes.DEFAULT_TYPE): Контекст обновления
        """
        message = update.effective_message
        try:
            if message.media_group_id:
                await self._handle_media_group(message, context)
            else:
                await self.handle_single(message, context)
        except Exception as e:
            raise e

    async def handle_single(
        self, message: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработка одиночного сообщения

        Args:
            message (Update): Сообщение от Telegram
            context (ContextTypes.DEFAULT_TYPE): Контекст обновления

        """
        content, files = await self._process_message(message, context)
        await self.discord.send(content, files)

    async def _handle_media_group(
        self, message: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработка группы медиа сообщений

        Args:
            message (Update): Сообщение от Telegram
            context (ContextTypes.DEFAULT_TYPE): Контекст обновления

        """
        async with self.lock:
            media_group_id = message.media_group_id
            if media_group_id not in [
                m.message_id for m in self.media_groups[media_group_id]
            ]:
                self.media_groups[media_group_id].append(message)

            if len(self.media_groups[media_group_id]) == 1:
                asyncio.create_task(self._process_media_group(media_group_id, context))

    async def _process_media_group(
        self, media_group_id, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработка группы медиа сообщений

        Args:
            media_group_id (str): ID группы медиа сообщений
            context (ContextTypes.DEFAULT_TYPE): Контекст обновления

        """
        await asyncio.sleep(5)

        async with self.lock:
            messages = self.media_groups.pop(media_group_id, [])

        content = ""
        files = []
        for msg in messages:
            caption, new_files = await self._process_message(msg, context)
            content = caption or content
            files.extend(new_files)

        if files:
            await self.discord.send(content, files)

    async def _process_message(
        self, message: str, context: ContextTypes.DEFAULT_TYPE
    ) -> Tuple[str, List[File]]:
        """Обработка сообщения

        Args:
            message (str): Сообщение от Telegram
            context (ContextTypes.DEFAULT_TYPE): Контекст обновления
        Returns:
            Tuple[str, List[File]]: Кортеж с текстом сообщения и списком файлов
        """
        logger.info("Processing message")
        content = message.caption or message.text or ""
        files = []
        forward_info = []
        forward_postfix = "💬  "

        # TODO: Разбить на стратегии

        if message.forward_origin:
            logger.info("Forwarded message found")
            origin = message.forward_origin
            if isinstance(origin, MessageOriginChannel):
                channel = origin.chat

                if channel.username:

                    name = f"{channel.title}" if channel.title else "Unknown Channel"
                    link = f"https://t.me/{channel.username}/{origin.message_id}"
                    channel_link = f"[{name}]({link})"
                    forward_info.append(f"{forward_postfix}{channel_link}")
                else:
                    forward_info.append(f"{forward_postfix}{origin.chat.title}")

            if forward_info:
                forward_text = "\n".join(forward_info)
                if content:
                    content = f"{forward_text}\n\n{content}"
                else:
                    content = forward_text

        if message.photo:
            logger.info("Photo found")
            file_id = message.photo[-1].file_id
            file_data = await download_media(file_id, context.bot)
            files.append(
                File(
                    io.BytesIO(file_data),
                    filename=f"nya.jpg",
                )
            )

        if message.animation:
            logger.info("Animation found")
            file_id = message.animation.file_id
            file_data = await download_media(file_id, context.bot)
            gif_data = await convert_mp4_to_gif(file_data)
            files.append(
                File(
                    io.BytesIO(gif_data),
                    filename=f"nya.gif",
                )
            )

        if message.video:
            logger.info("Video found")
            file_id = message.video.file_id
            file_data = await download_media(file_id, context.bot)
            files.append(
                File(
                    io.BytesIO(file_data),
                    filename=f"nya.mp4",
                )
            )

        return content, files
