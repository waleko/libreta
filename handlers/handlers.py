from typing import List

from telegram import Update
from telegram.ext import Handler, CallbackContext, ConversationHandler

from strings import Strings
from utils.dao import Dao

handlers: List[Handler] = []


def register_unprotected_handler(handler: Handler):
    """
    Adds given handler to `Bot`
    """
    handlers.append(handler)


def add_authguard_to_handler(handler: Handler) -> Handler:
    """
    Transforms handler to be accessible only to invited users.

    :param handler: handler without authguard
    :return: same handler with an authguard
    """
    # if handler is a ConversationHandler, there is no `.callback`
    if isinstance(handler, ConversationHandler):
        # recursively add authguard to every entry point
        new_entry_points = [add_authguard_to_handler(entry_point) for entry_point in handler.entry_points]
        # construct new handler
        new_handler = ConversationHandler(
            new_entry_points,
            handler.states,
            handler.fallbacks,
            handler.allow_reentry,
            handler.per_chat,
            handler.per_user,
            handler.per_message,
            handler.conversation_timeout,
            handler.name,
            handler.persistent,
            handler.map_to_parent,
            handler.run_async
        )
        return new_handler
    else:
        # get default callback
        callback = handler.callback

        # custom callback
        def auth_guard_callback(update: Update, context: CallbackContext):
            # check user auth status
            if Dao.is_user_authorized(update.effective_user):
                # if authenticated, continue execution
                return callback(update, context)
            else:
                # if not authenticated, reply with failed
                update.effective_message.reply_text(Strings.unauthenticated)

        # apply custom callback
        handler.callback = auth_guard_callback
        return handler


def register_protected_handler(handler: Handler):
    """
    Adds auth guard to handler and dds new (protected) handler to `Bot`
    """
    register_unprotected_handler(add_authguard_to_handler(handler))
