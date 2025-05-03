from typing import Optional

from telegram.error import BadRequest, TelegramError

from app.utils.logging import get_logger
from app.config import get_settings
from app.utils.errors import FileTooLargeError, MediaDownloadError


logger = get_logger(__name__)


async def download_media(file_id: str, bot) -> bytes:
    """Просто скачивает медиа из Telegram.

    Args:
        file_id (str): ID файла в Telegram.
        bot: Объект бота Telegram.
    Returns:
        bytes: Скачанный файл в виде байтового массива.
    """

    settings = get_settings()
    try:
        tg_file = await bot.get_file(file_id)
        file_size = tg_file.file_size
        if file_size > settings.telegram.max_file_size:
            logger.error(f"File {file_id} is too large: {file_size} bytes.")
            raise FileTooLargeError(file_id, file_size, settings.telegram.max_file_size)

        logger.info(
            "Downloading...",
            extra={
                "file_id": file_id,
                "file_size": file_size,
                "max_size": settings.telegram.max_file_size,
            },
        )
        file_bytes = await tg_file.download_as_bytearray()

        return file_bytes
    except BadRequest as e:
        if "File is too big" in str(e):
            logger.error(
                "Telegram API file size limit exceeded.",
                extra={"file_id": file_id, "max_size": settings.telegram.max_file_size},
            )
            raise FileTooLargeError(
                file_id, 0, settings.telegram.max_file_size
            ) from None
        logger.error("Telegram API error", extra={"file_id": file_id, "error": str(e)})
        raise MediaDownloadError(file_id, "Telegram API request error")
    except TelegramError as e:
        logger.error(
            "Telegram client error", extra={"file_id": file_id, "error": str(e)}
        )
        raise MediaDownloadError(file_id, "Telegram client error")
    except Exception as e:
        logger.error(
            "Unexpected error in download_media",
            extra={"file_id": file_id, "error": str(e)},
        )
        raise MediaDownloadError(file_id, "Unexpected error")
