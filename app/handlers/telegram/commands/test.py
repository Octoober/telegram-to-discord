import logging

from telegram import Update
from telegram.ext import ContextTypes


logger = logging.getLogger(__name__)


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Проверка работы бота."""
    user = update.effective_user
    await update.message.reply_text(text="Я работаю!")
    logger.info("User %s started the bot", user.username)
