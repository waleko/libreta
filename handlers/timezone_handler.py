"""
Handler for specifying user timezone.

User timezone in turn is needed to figure out, what day user is sending content for.
"""
from enum import Enum, auto
from typing import List, Dict

import pytz
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, RegexHandler

from handlers.handlers import register_protected_handler
from handlers.misc import cancel
from strings import Strings
from utils.dao import Dao

# parse timezones

# get common timezones
timezones = pytz.common_timezones
# group by continent
structured_timezones: Dict[str, List[str]] = {}
for tz in timezones:
    # skip UTC, GMT etc, as they are not geographical places
    if '/' not in tz:
        continue
    #  parse into continent and city
    #  `maxsplit` is needed as timezones with three parts exist,
    #  e.g. `America/Kentucky/Louisville`
    cont, city = tz.split('/', maxsplit=1)
    # save to dict
    structured_timezones.setdefault(cont, [])
    structured_timezones[cont].append(city)


class TimezoneStates(Enum):
    """
    States for timezone handler
    """
    WAIT_CONTINENT = auto()
    WAIT_CITY = auto()


def continent_select(update: Update, _: CallbackContext):
    """
    Prompts user to select their continent (or similar, e.g. US or India) using a keyboard.
    """
    # init keyboard
    keyboard = [[KeyboardButton(continent)] for continent in sorted(structured_timezones.keys())]
    # reply to user
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text(Strings.timezone_select_and_start, reply_markup=reply_markup)
    return TimezoneStates.WAIT_CONTINENT


def city_select(update: Update, context: CallbackContext):
    """
    Prompts user to select exact timezone for continent specified earlier
    """
    # get continent selected by user
    selected_continent = update.message.text
    # check the validity of input
    if selected_continent not in structured_timezones:
        # reply with failed, send back to `continent_select`
        update.effective_message.reply_text(Strings.entered_continent_invalid)
        return continent_select(update, context)
    # save continent in context
    context.user_data['tz_cont'] = selected_continent

    # init keyboard
    keyboard = [[KeyboardButton(city)] for city in sorted(structured_timezones[selected_continent])]
    # reply to user
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text(Strings.please_enter_city, reply_markup=reply_markup)
    return TimezoneStates.WAIT_CITY


def timezone_confirm(update: Update, context: CallbackContext):
    """
    Handles user specified timezone
    """
    # get user selected city
    selected_city = update.message.text
    # construct timezone string
    resulting_timezone = f"{context.user_data['tz_cont']}/{selected_city}"
    # check the validity of input
    if resulting_timezone not in timezones:
        # reply with failed, send back to `continent_select`
        update.effective_message.reply_text(Strings.timezone_invalid)
        return continent_select(update, context)

    # save constructed timezone to db
    Dao.set_user_timezone(update.effective_user, pytz.timezone(resulting_timezone))
    # reply to user
    update.effective_message.reply_text(Strings.timezone_set(resulting_timezone))
    return ConversationHandler.END


set_timezone_handler = ConversationHandler(
    entry_points=[CommandHandler('timezone', continent_select), CommandHandler('start', continent_select)],
    states={
        TimezoneStates.WAIT_CONTINENT: [RegexHandler(r"^\w+$", city_select)],
        TimezoneStates.WAIT_CITY: [RegexHandler(r"^\w+$", timezone_confirm)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

register_protected_handler(set_timezone_handler)
