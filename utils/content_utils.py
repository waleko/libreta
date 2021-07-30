from typing import Callable, Any

from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters


def get_content_message_handler_for_callback(callback: Callable[[Update, CallbackContext], Any]) -> MessageHandler:
    """
    Creates a universal message handler, that catches all messages, that should be considered as diary content.

    :param callback: Function to be ran when such message is caught
    :return: `MessageHandler`
    """
    return MessageHandler(
        (Filters.update.message | Filters.update.edited_message) &
        (Filters.text | Filters.photo | Filters.document),
        callback
    )
