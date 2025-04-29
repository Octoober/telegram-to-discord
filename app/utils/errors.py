class FileTooLargeError(Exception):
    """Для обработки ошибок, связанных с размером файла."""

    def __init__(self, file_id: str, file_size: int, max_size: int):
        """Инициализация ошибки.

        Args:
            file_id (str): ID файла
            file_size (int): Размер файла
            max_size (int): Максимальный размер файла
        """
        self.file_id = file_id
        self.file_size = file_size
        self.max_size = max_size
        message = (
            f"File {file_id} is too large: {file_size} bytes. "
            f"Max size is {max_size} bytes."
        )
        super().__init__(message)


class MediaDownloadError(Exception):
    """Для обработки ошибок, связанных с загрузкой медиа."""

    def __init__(self, file_id: str, message: str):
        """Инициализация ошибки.

        Args:
            file_id (str): ID файла
            message (str): Сообщение об ошибке
        """
        self.file_id = file_id
        super().__init__(message)
