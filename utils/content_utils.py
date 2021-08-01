from typing import Callable, Any

from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters

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
