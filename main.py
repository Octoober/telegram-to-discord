import io
import logging
import tempfile
import asyncio
from collections import defaultdict

from moviepy import VideoFileClip

from telegram import Update, Message
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    filters,
    MessageHandler,
)
from discord import SyncWebhook, File


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1362802614806249474/VWxXp4DncmS4OM9nqs-dBbWiK4ep-DhU5hGzrfxp8QE773WGl_ua8YjyURb6M-ApSf5I"
TELEGRAM_BOT_TOKEN = "6101653458:AAH_IHKib0LwWUh4dILJ9xEXm8JzrA3z-Zk"


media_groups = defaultdict(list)
lock = asyncio.Lock()


async def convert_mp4_to_gif(file_data: bytes) -> bytes:
    """Конвертирует mp4 в gif."""
    # временное хранилище для файла
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_in:
        tmp_in.write(file_data)
        tmp_in_path = tmp_in.name

    # загрузка видео
    clip = VideoFileClip(tmp_in_path)

    # временное хранилище для gif
    with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmp_out:
        tmp_out_path = tmp_out.name

    # конвертация в gif
    clip.write_gif(tmp_out_path, fps=15)

    with open(tmp_out_path, "rb") as f:
        gif_data = f.read()

    return gif_data


async def download_telegram_media(file_id: str, bot) -> bytes:
    """Просто скачивает медиа из Telegram."""
    logger.info("Downloading file with ID: %s", file_id)
    tg_file = await bot.get_file(file_id)
    return await tg_file.download_as_bytearray()


async def forward_to_discord(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Отправляет сообщение в Discord."""
    message = update.effective_message
    try:
        if not message.media_group_id:
            # отправка одиночного сообщения
            await process_single_message(message, context)
            return

        async with lock:
            # отправка медиа группы
            media_group_id = message.media_group_id

            # проверяет есть ли медиа с таким id в группе
            if not any(
                msg.message_id == message.message_id
                for msg in media_groups[media_group_id]
            ):
                media_groups[media_group_id].append(message)

            if len(media_groups[media_group_id]) == 1:
                asyncio.create_task(process_media_group(media_group_id, context))
    except Exception as e:
        logger.error("Error forwarding message to Discord: %s", e)


async def process_single_message(message: Message, context: ContextTypes.DEFAULT_TYPE):
    """Процесс одиночного сообщения."""
    webhook = SyncWebhook.from_url(DISCORD_WEBHOOK_URL)
    content = message.caption or ""
    files = []

    try:
        if message.photo:
            logger.info("Photo found")
            # Фото в макс. разрешении
            file_id = message.photo[-1].file_id
            file_data = await download_telegram_media(file_id, context.bot)
            files.append(
                File(
                    io.BytesIO(file_data),
                    filename=f"nya.jpg",
                )
            )

        if message.video:
            logger.info("Video found")
            # Видео в макс. разрешении
            file_id = message.video.file_id
            file_data = await download_telegram_media(file_id, context.bot)
            files.append(
                File(
                    io.BytesIO(file_data),
                    filename=f"{message.video.file_id}.mp4",
                )
            )

        if message.animation:
            logger.info("Animation found")
            # Анимация в макс. разрешении
            file_id = message.animation.file_id
            file_data = await download_telegram_media(file_id, context.bot)
            gif_data = await convert_mp4_to_gif(file_data)
            files.append(
                File(
                    io.BytesIO(gif_data),
                    filename=f"{message.animation.file_id}.gif",
                )
            )

        if content or files:
            # если есть текст или файлы, отправляем в Discord
            logger.info("Forwarding message to Discord: %s", content)
            webhook.send(
                content=content,
                username="Telegram Bot",
                files=files,
                wait=True,
            )
            logger.info("Message sent to Discord successfully")
    except Exception as e:
        raise e


async def process_media_group(
    media_group_id: str, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Процесс медиа группы."""
    await asyncio.sleep(1)

    async with lock:
        message = media_groups.get(media_group_id, [])
        if not message:
            return

        # убираем дубликаты
        message = list({msg.message_id: msg for msg in message}.values())
        content = ""
        files = []

        for msg in message:
            if msg.caption:
                content = msg.caption

            if msg.photo:
                logger.info("Photo found")
                # Фото в макс. разрешении
                file_id = msg.photo[-1].file_id
                file_data = await download_telegram_media(file_id, context.bot)
                files.append(
                    File(
                        io.BytesIO(file_data),
                        filename=f"nya.jpg",
                    )
                )

            if msg.video:
                logger.info("Video found")
                # Видео в макс. разрешении
                file_id = msg.video.file_id
                file_data = await download_telegram_media(file_id, context.bot)
                files.append(
                    File(
                        io.BytesIO(file_data),
                        filename=f"{msg.video.file_id}.mp4",
                    )
                )

            if msg.animation:
                logger.info("Animation found")
                # Анимация в макс. разрешении
                file_id = msg.animation.file_id
                file_data = await download_telegram_media(file_id, context.bot)
                gif_data = await convert_mp4_to_gif(file_data)
                files.append(
                    File(
                        io.BytesIO(gif_data),
                        filename=f"{msg.animation.file_id}.gif",
                    )
                )
        if files:
            # если есть файлы, отправляем в Discord
            logger.info("Forwarding media group to Discord: %s", content)
            webhook = SyncWebhook.from_url(DISCORD_WEBHOOK_URL)
            webhook.send(
                content=content,
                username="Telegram Bot",
                files=files,
                wait=True,
            )
            logger.info("Media group sent to Discord successfully")

        del media_groups[media_group_id]


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Проверка работы бота."""
    user = update.effective_user
    await update.message.reply_text(text="Я работаю!")
    logger.info("User %s started the bot", user.username)


def main() -> None:
    """Стартует бота."""
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("test", test))

    # следить только за постами на канале
    application.add_handler(
        MessageHandler(filters.ChatType.CHANNEL, forward_to_discord)
    )

    application.run_polling()


if __name__ == "__main__":
    main()
