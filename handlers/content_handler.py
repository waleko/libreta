import datetime
import logging
import re
from enum import Enum, auto
from typing import Optional

from telegram import Update, ReplyKeyboardMarkup, Message
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, RegexHandler, MessageHandler, Filters

from handlers import cancel
from handlers.handlers import register_protected_handler
from strings import Strings
from utils.content_utils import get_content_message_handler_for_callback
from utils.dao import Dao


class ContentEnums(Enum):
    AWAITING_DATE = auto()
    AWAITING_CONTENT = auto()
    AWAITING_CONFIRMATION = auto()


def save_message_content_by_date(update: Update, _: CallbackContext, user_date: datetime.date) -> None:
    """
    Saves content from update into db

    :param user_date: Date that will be associated with content
    """
    # get message as dict (to be saved)
    obj = update.effective_message.to_dict()
    # upload to db
    message_id = update.effective_message.message_id
    Dao.publish(update.effective_user, user_date, message_id, obj)
    # reply to user
    update.effective_message.reply_text(Strings.published(user_date), reply_to_message_id=message_id)


def prompt_content_input(update: Update, _: CallbackContext):
    """
    Prompts user to enter content
    """
    update.effective_message.reply_text(Strings.please_enter_content)
    return ContentEnums.AWAITING_CONTENT


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
    entry_points=[CommandHandler('yesterday', prompt_content_input)],
    states={
        ContentEnums.AWAITING_CONTENT: [get_content_message_handler_for_callback(yesterday_handler)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

register_protected_handler(yesterday_conv_handler)


def time_selection(update: Update, _: CallbackContext):
    """
    Ask user for their desired date to be associated with content
    """
    update.effective_message.reply_text(Strings.please_enter_date)
    return ContentEnums.AWAITING_DATE


def date_entering(update: Update, context: CallbackContext):
    """
    Process the date for being uploaded to.
    """
    # get user input
    date_str = update.effective_message.text
    # validate ISO format
    try:
        # try to create a `date` from it
        _ = datetime.date.fromisoformat(date_str)
    except ValueError as e:
        # if failed to create `date`, reply with failed
        update.effective_message.reply_text(Strings.try_again_check_validity)
        # log client error
        logging.debug(e.__str__())
        # prompt to try again
        return ContentEnums.AWAITING_DATE
    # save user input for the next step
    context.user_data["custom_date"] = date_str
    # prompt to enter diary content
    update.effective_message.reply_text(Strings.please_enter_content)
    return ContentEnums.AWAITING_CONTENT


def custom_date_content_handler(update: Update, context: CallbackContext):
    """
    Upload diary content for given date
    """
    # check the presense of `custom_date`
    ud: Optional[dict] = context.user_data
    if ud is None or "custom_date" not in ud:
        # if not, something went very wrong
        update.effective_message.reply_text(Strings.server_error_and_cancelled)
        # log error
        logging.error("No custom_date in user data!")
        return ConversationHandler.END
    # get custom date
    user_date = datetime.date.fromisoformat(ud["custom_date"])
    # save message content
    save_message_content_by_date(update, context, user_date)
    return ConversationHandler.END


custom_date_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('customdate', time_selection)],
    states={
        ContentEnums.AWAITING_DATE: [RegexHandler(re.compile(r"^\d{4}-\d{2}-\d{2}$"), date_entering)],
        ContentEnums.AWAITING_CONTENT: [get_content_message_handler_for_callback(custom_date_content_handler)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

register_protected_handler(custom_date_conv_handler)


def content_confirmation(update: Update, context: CallbackContext):
    context.user_data["content_awaiting_confirmation"] = update.effective_message.to_dict()

    message_id = update.effective_message.message_id
    keyboard = [[Strings.Yes, Strings.No]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.effective_message.reply_text(Strings.confirm_save, reply_markup=reply_markup, reply_to_message_id=message_id)
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
    Dao.publish(update.effective_user, user_datetime, message.message_id, message.to_dict())
    # answer user
    update.effective_message.reply_text(Strings.published(user_datetime), reply_to_message_id=message.message_id)
    return ConversationHandler.END


# INFO: this content handler has to come very last, as this content handler accepts (almost) any message
register_protected_handler(ConversationHandler(
    entry_points=[get_content_message_handler_for_callback(content_confirmation)],
    states={
        ContentEnums.AWAITING_CONFIRMATION: [MessageHandler(Filters.text, content_handler_with_confirmation)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
))
