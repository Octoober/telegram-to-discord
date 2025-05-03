import io
import asyncio
from collections import defaultdict
from typing import List, Tuple, Optional


from telegram import Update, Message, MessageOriginChannel, MessageOriginUser
from telegram.ext import ContextTypes
from discord import File

from app.services.discord import DiscordService
from app.services.media_service import MediaService
from app.models.media_group import MediaGroup
from app.utils.logging import get_logger

from app.config import get_settings, Settings


class TelegramMediaHandler:
    def __init__(
        self,
        media_service: MediaService,
        discord_service: DiscordService,
        settings: Settings,
    ) -> None:
        self.media_groups: dict[str, MediaGroup] = {}
        self.media_service = media_service
        self.discord = discord_service
        self.settings = settings

        self.lock = asyncio.Lock()
        self.logger = get_logger(__name__)

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработка сообщения от Telegram

        Args:
            update (Update): Обновление от Telegram
            context (ContextTypes.DEFAULT_TYPE): Контекст обновления
        """
        msg: Message = update.effective_message
        try:
            if msg.media_group_id:
                self.logger.info("Processing media group")
                await self._handle_media_group(msg, context)
            else:
                self.logger.info("Processing single message")
                await self._process_and_send([msg], context)
        except Exception as e:
            self.logger.error(
                f"Error processing message: {e}",
                extra={
                    "message_id": msg.message_id,
                    "chat_id": msg.chat.id,
                    "user_id": msg.from_user.id if msg.from_user else None,
                },
            )
            raise

    async def _handle_media_group(
        self, msg: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработка группы медиа сообщений

        Args:
            message (Update): Сообщение от Telegram
            context (ContextTypes.DEFAULT_TYPE): Контекст обновления

        """
        async with self.lock:
            group_id = msg.media_group_id
            group = self.media_groups.setdefault(group_id, MediaGroup())
            if msg.message_id in group.ids:
                return
            group.messages.append(msg)
            group.ids.add(msg.message_id)
            if len(group.messages) == 1:
                asyncio.create_task(self._schedule_flush(group_id, context))

    async def _schedule_flush(
        self, group_id: str, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Запланировать отправку группы медиа

        Args:
            group_id (str): ID группы медиа
            context (ContextTypes.DEFAULT_TYPE): Контекст обновления
        """
        await asyncio.sleep(5)
        async with self.lock:
            group = self.media_groups.pop(group_id, [])

        if group:
            await self._process_and_send(group.messages, context)

    def _compose_forward_text(self, msg: Message) -> Optional[str]:
        origin = msg.forward_origin
        if not origin:
            return None

        postfix = self.settings.discord.message.forward_postfix

        # Репост из канала
        if isinstance(origin, MessageOriginChannel):
            channel = origin.chat
            name = channel.title or channel.username or "Unknown Channel"

            if channel.username:
                # Если есть username, то используем его
                link = f"https://t.me/{channel.username}/{origin.message_id}"
                return f"{postfix}[{name}]({link})"
            else:
                # Если нет username, то используем ID
                return f"{postfix}{name}"

        # Репост от пользователя
        if isinstance(origin, MessageOriginUser):
            user = origin.sender_user
            name = user.first_name or "Unknown User"
            if user.link:
                # Если есть username, то используем его с ссылкой
                return f"{postfix}[{name}]({user.link})"

            # Если нет username, то используем только имя
            return f"{postfix}{name}"

        # Какой-то редкий случай
        return None

    async def _process_and_send(
        self, messages: List[Message], context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработка и отправка сообщений"""

        first_msg: Message = messages[0]
        forward = self._compose_forward_text(first_msg)
        content = (first_msg.caption or first_msg.text or "").strip()

        if forward:
            content = f"{forward}\n\n{content}"

        payloads = []
        for msg in messages:
            payloads.extend(await self.media_service.build_payloads(msg, context))

        self.logger.info("Sending to Discord", extra={"payloads": payloads})
        await self.discord.send(content, payloads)
