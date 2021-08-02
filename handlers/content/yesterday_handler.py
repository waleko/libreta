import datetime

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler

from handlers import cancel, register_protected_handler
from utils import Dao
from utils.content_utils import save_message_content_by_date, prompt_content_input, get_content_message_handler, \
    ContentEnums


def yesterday_handler(update: Update, context: CallbackContext):
    """
    Diary content upload handler. Uploads incoming messages to db as a note for yesterday.
    """
    # get user timezone
    user_timezone = Dao.get_user_timezone(update.effective_user)
    # calculate time at user's
    user_datetime = update.effective_message.date.astimezone(user_timezone)
    # get yesterday
    user_yesterday = user_datetime - datetime.timedelta(days=1)
    # save message content
    save_message_content_by_date(update, context, user_yesterday)
    return ConversationHandler.END


# register `/yesterday` handler
yesterday_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("yesterday", prompt_content_input)],
    states={
        ContentEnums.AWAITING_CONTENT: [
            get_content_message_handler(yesterday_handler)
        ]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

register_protected_handler(yesterday_conv_handler)
