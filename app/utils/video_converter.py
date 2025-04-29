# import math
import tempfile
import asyncio
import subprocess

from typing import Optional
from pathlib import Path
from app.config import get_settings
from app.utils.logging import get_logger


logger = get_logger(__name__)


async def convert_mp4_to_gif(file_data: bytes) -> bytes:
    """Конвертирует mp4 в gif.

    Args:
        file_data (bytes): Данные файла mp4 в виде байтового массива.
    Returns:
        bytes: Данные файла gif в виде байтового массива.
    """

    settings = get_settings()
    temp_dir = Path(settings.TEMP_PATH)
    temp_dir.mkdir(parents=True, exist_ok=True)

    input_path: Optional[Path] = None
    output_path: Optional[Path] = None
    try:
        # Сохраняем входящий файл во временное хранилище
        with tempfile.NamedTemporaryFile(
            dir=temp_dir, suffix=".mp4", delete=False
        ) as tmp_in:
            input_path = Path(tmp_in.name)
            tmp_in.write(file_data)
            logger.debug(f"Saved input video to {input_path}")

        # Подготавливаем путь для гиф
        with tempfile.NamedTemporaryFile(
            dir=temp_dir, suffix=".gif", delete=False
        ) as tmp_out:
            output_path = Path(tmp_out.name)
            logger.debug(f"Preparing output gif path: {output_path}")

        def _convert():
            """Конвертирует mp4 в gif с помощью FFmpeg."""
            cmd = [
                "ffmpeg",
                "-y",  # Перезапись без подтверждения
                "-i",
                str(input_path),
                "-vf",
                "fps=10,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
                "-loop",
                "0",
                str(output_path),
            ]

            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr.decode()}")
                raise RuntimeError(
                    f"FFmpeg conversion failed: {result.stderr.decode()}"
                )

        # Запускаем конвертацию в отдельном потоке
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _convert)

        if not output_path.exists():
            # Если выходной файл не существует, это может быть ошибкой
            raise FileNotFoundError(f"Output file not found: {output_path}")

        # Читаем и возвращаем данные из выходного файла
        return output_path.read_bytes()

    finally:
        # В конце удаляет временные файлы
        for path in (input_path, output_path):
            if isinstance(path, Path) and path.exists():
                try:
                    path.unlink()
                    logger.debug(f"Deleted temporary file: {path}")
                except Exception as e:
                    logger.error(f"Error deleting temporary file {path}: {e}")
