import datetime
from textwrap import dedent
from typing import Union


class Strings(object):
    """
    Object storing strings for UI (bot replies)
    """

    start = "Welcome to Libreta!"
    updated = "Your changes have been saved"
    Yes = "Yes"
    No = "No"
    confirm_save = "Do you actually want to save this?"
    please_enter_content = "Please enter content:"
    server_error_and_cancelled = (
        "Something went wrong! Operation has been cancelled. Please try again later."
    )
    try_again_check_validity = "Please try again. Check that your input is correct."
    please_enter_date = dedent(
        """\
    Please enter date that the content will be associated with:
    
    Please use ISO format (e.g. 2021-07-29)."""
    )
    __published = "Saved for"
    cancelled = "Cancelled"
    timezone_invalid = "This timezone is invalid. Please try again or /cancel."
    please_enter_city = "Please select your city timezone, or /cancel to cancel:"
    entered_continent_invalid = (
        "This continent is invalid. Please try again or /cancel."
    )
    timezone_select = "Please select a continent, or /cancel to cancel:"
    unauthenticated = "Unfortunately, you are not authorized to use this bot"
    __timezone_set = "Your timezone has been set to"

    @classmethod
    def timezone_set(cls, resulting_timezone: str) -> str:
        return f"{cls.__timezone_set} {resulting_timezone}."

    @classmethod
    def published(cls, message_date: Union[datetime.date, str]):
        date_str: str
        if isinstance(message_date, datetime.date):
            date_str = message_date.strftime("%Y-%m-%d")
        else:
            date_str = message_date
        return f"{cls.__published} {date_str}"
