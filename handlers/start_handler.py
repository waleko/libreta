from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from handlers.handlers import register_unprotected_handler
from strings import Strings


def start_handler(update: Update, _: CallbackContext):
    update.effective_message.reply_text(Strings.start)


register_unprotected_handler(CommandHandler("start", start_handler))
