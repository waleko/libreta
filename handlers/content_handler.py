import datetime

from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters

from firebase.dao import Dao
from handlers.handlers import register_unprotected_handler
from strings import Strings


def content_handler(update: Update, _: CallbackContext):
    """
    New diary content upload handler. Uploads incoming messages to db as a note.
    """
    # get message as dict (to be saved)
    obj = update.effective_message.to_dict()
    # get user timezone
    user_timezone = Dao.get_user_timezone(update.effective_user)
    # calculate time at user's
    user_time = datetime.datetime.now(tz=user_timezone)
    # get user today's date
    user_today = user_time.date()
    # upload to db
    Dao.publish(update.effective_user, user_today, update.effective_message.message_id, obj)
    # reply to user
    update.effective_message.reply_text(Strings.published)


register_unprotected_handler(MessageHandler(
    (Filters.update.message | Filters.update.edited_message) &
    (Filters.text | Filters.photo | Filters.document),
    content_handler
))
