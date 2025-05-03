from typing import List, Set
from dataclasses import dataclass, field

from telegram import Message


@dataclass
class MediaGroup:
    """
    Носитель медиа группы для отправки в дискорд

    Attributes:
        ids (Set[int]): Набор айдишников сообщений
        messages (List[Message]): Список сообщений
    """

    ids: Set[int] = field(default_factory=set)
    messages: List[Message] = field(default_factory=list)
