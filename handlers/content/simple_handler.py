from telegram import Update, ReplyKeyboardMarkup, Message
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, Filters, CommandHandler

from handlers import register_protected_handler, cancel
from strings import Strings
from utils import Dao
from utils.content_utils import ContentEnums, get_content_update_handler, get_content_message_handler


def content_confirmation(update: Update, context: CallbackContext):
    context.user_data[
        "content_awaiting_confirmation"
    ] = update.effective_message.to_dict()

    message_id = update.effective_message.message_id
    keyboard = [[Strings.Yes, Strings.No]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.effective_message.reply_text(
        Strings.confirm_save, reply_markup=reply_markup, reply_to_message_id=message_id
    )
    return ContentEnums.AWAITING_CONFIRMATION


def content_handler_with_confirmation(update: Update, context: CallbackContext):
    answer = update.effective_message.text
    if answer != Strings.Yes:
        update.effective_message.reply_text(Strings.cancelled)
        return ConversationHandler.END
    obj = context.user_data["content_awaiting_confirmation"]

    # get user timezone
    user_timezone = Dao.get_user_timezone(update.effective_user)
    # get content message from context
    message = Message.de_json(obj, context.bot)
    # calculate time at user's
    user_datetime = message.date.astimezone(user_timezone)
    # publish
    Dao.publish(
        update.effective_user, user_datetime, message
    )
    # answer user
    update.effective_message.reply_text(
        Strings.published(user_datetime), reply_to_message_id=message.message_id
    )
    return ConversationHandler.END


# INFO: this content handler has to come very last, as this content handler accepts (almost) any message
register_protected_handler(
    ConversationHandler(
        entry_points=[get_content_message_handler(content_confirmation)],
        states={
            ContentEnums.AWAITING_CONFIRMATION: [
                MessageHandler(Filters.text, content_handler_with_confirmation)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
)
