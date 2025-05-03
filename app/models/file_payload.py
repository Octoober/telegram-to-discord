from dataclasses import dataclass


@dataclass
class FilePayload:
    """
    Носитель файла для отправки в дискорд

    Attributes:
        data (str): Сырые данные файла
        filename (str): Имя файла
    """

    data: bytes
    filename: str
