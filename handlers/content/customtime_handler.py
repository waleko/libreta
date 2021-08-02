import datetime
import logging
import re
from typing import Optional

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, RegexHandler

from handlers import cancel, register_protected_handler
from strings import Strings
from utils.content_utils import ContentEnums, save_message_content_by_date, get_content_message_handler


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
    entry_points=[CommandHandler("customdate", time_selection)],
    states={
        ContentEnums.AWAITING_DATE: [
            RegexHandler(re.compile(r"^\d{4}-\d{2}-\d{2}$"), date_entering)
        ],
        ContentEnums.AWAITING_CONTENT: [
            get_content_message_handler(custom_date_content_handler)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

register_protected_handler(custom_date_conv_handler)
