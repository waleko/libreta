import datetime
from enum import Enum, auto
from typing import Callable, Any

from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters

from strings import Strings
from utils import Dao

content_filters = (Filters.text & (~Filters.command)) | Filters.photo | Filters.document


def get_content_message_handler(
    callback: Callable[[Update, CallbackContext], Any]
) -> MessageHandler:
    """
    Creates a universal message handler, that catches all messages, that should be considered as diary content.

    :param callback: Function to be ran when such message is caught
    :return: `MessageHandler`
    """
    return MessageHandler(
        Filters.update.message
        & content_filters,
        callback,
    )


def get_content_update_handler(
    callback: Callable[[Update, CallbackContext], Any]
) -> MessageHandler:
    """
    Creates a message update handler, that catches diary content update.

    :param callback: Function to be ran when such message is caught
    :return: `MessageHandler`
    """
    return MessageHandler(
        Filters.update.edited_message
        & content_filters,
        callback,
    )


class ContentEnums(Enum):
    AWAITING_DATE = auto()
    AWAITING_CONTENT = auto()
    AWAITING_CONFIRMATION = auto()


def save_message_content_by_date(
    update: Update, _: CallbackContext, user_date: datetime.date
) -> None:
    """
    Saves content from update into db

    :param user_date: Date that will be associated with content
    """
    # upload to db
    message_id = update.effective_message.message_id
    Dao.publish(update.effective_user, user_date, update.effective_message)
    # reply to user
    update.effective_message.reply_text(
        Strings.published(user_date), reply_to_message_id=message_id
    )


def prompt_content_input(update: Update, _: CallbackContext):
    """
    Prompts user to enter content
    """
    update.effective_message.reply_text(Strings.please_enter_content)
    return ContentEnums.AWAITING_CONTENT
