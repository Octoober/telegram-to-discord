import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logget(
    log_file: str = "app.log",
    log_level: str = "INFO",
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
    libs: Optional[list[str]] = None,
) -> None:
    """Настраивает логирование в файл и на консоль.

    Args:
        log_file (str): Путь к файлу лога.
        log_level (str): Уровень логирования.
        max_bytes (int): Максимальный размер файла лога в байтах.
        backup_count (int): Количество резервных файлов лога.
        libs (Optional[list[str]]): Список библиотек для настройки уровня логирования.
    """
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        filename=log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )

    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # Обработчик для консоли
    console_bandler = logging.StreamHandler(sys.stdout)
    console_bandler.setFormatter(formatter)
    console_bandler.setLevel("INFO")

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_bandler)

    for lib in libs or []:
        logging.getLogger(lib).setLevel("WARNING")


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name)
