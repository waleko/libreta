from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from strings import Strings


def cancel(update: Update, _: CallbackContext):
    """
    Simple cancel handler
    """
    # reply and hide any current keyboard
    update.effective_message.reply_text(Strings.cancelled, reply_markup={"remove_keyboard": True})
    return ConversationHandler.END
