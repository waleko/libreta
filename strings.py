import i18n


class Strings(object):
    """
    Object storing strings for UI (bot replies)
    """
    published = "Your changes have been published!"
    cancelled = "Cancelled"
    timezone_invalid = "This timezone is invalid. Please try again or /cancel."
    please_enter_city = "Please select your city timezone, or /cancel to cancel:"
    entered_continent_invalid = "This continent is invalid. Please try again or /cancel."
    timezone_select_and_start = "Please select a continent, or /cancel to cancel:"
    unauthenticated = "Unfortunately, you are not authorized to use this bot"
    __timezone_set = "Your timezone has been set to"

    @classmethod
    def timezone_set(cls, resulting_timezone: str) -> str:
        return f"{cls.__timezone_set} {resulting_timezone}."
