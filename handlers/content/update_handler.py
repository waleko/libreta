from telegram import Update
from telegram.ext import CallbackContext

from handlers import register_protected_handler
from strings import Strings
from utils import Dao
from utils.content_utils import get_content_update_handler


def update_handler(update: Update, _: CallbackContext):
    has_been_updated = Dao.update_message(update.effective_user, update.effective_message)
    if has_been_updated:
        update.effective_message.reply_text(Strings.updated, reply_to_message_id=update.effective_message.message_id)


register_protected_handler(get_content_update_handler(update_handler))
