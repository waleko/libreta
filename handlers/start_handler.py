from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from handlers.handlers import register_handler


def start_handler(update: Update, _: CallbackContext):
    update.effective_message.reply_text("Hi!")


register_handler(CommandHandler("start", start_handler))
