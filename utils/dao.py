import datetime
import logging
import os
from datetime import date
from typing import Optional, Union

import pytz
from firebase_admin import db
from telegram import User, Message

# get db root, depending on whether app is running in production
db_root: str
if os.environ.get("DEBUG") is None:
    db_root = "libreta"  # production db
else:
    db_root = "libreta-test"  # test db


class Dao(object):
    """
    Data Access Object for realtime database.

    Implements API for saving content, checking user authorization status, etc.
    """

    root = db_root

    @classmethod
    def is_user_authorized(cls, user: Optional[User]) -> bool:
        """
        Checks whether user is authorized, i.e. whether he is present in `invited_users`.

        :param user: user to be checked
        :return: True if authorized and shall be permitted to use the bot, false otherwise.
        """
        if user is None:
            return False
        return db.reference(f"{cls.root}/invited_users/{user.id}").get() is not None

    @classmethod
    def has_published_on_date(cls, user: User, date: date) -> bool:
        """
        Checks whether user has published any content on given date.

        Used to notify him about this blank.

        :param date:
        :param user:
        :return:
        """
        date_str = date.__str__()
        return (
            db.reference(f"{cls.root}/users/{user.id}/by_date/{date_str}").get()
            is not None
        )

    @classmethod
    def publish(cls, user: User, today: date, message: Message):
        content = message.to_dict()
        message_id = message.message_id
        """
        Uploads content to the database.

        :param user: User that provided content
        :param today: Date to be associated with following content
        :param unique_message_id: Message id of content. If such content record exists, it will be overridden.
        :param content: User content as dict.
        """
        date_str = today.strftime("%Y-%m-%d")
        db.reference(
            f"{cls.root}/users/{user.id}/by_date/{date_str}/{message_id}"
        ).update(content)
        db.reference(
            f"{cls.root}/users/{user.id}/message_date"
        ).update({message_id: date_str})

    @classmethod
    def update_message(cls, user: User, edited_message: Message) -> bool:
        """
        Updates content in db for message

        :param user: User that has the message
        :param edited_message: message
        :return: `True` if updated successfully, `False` if this message is not diary content
        """
        message_id = edited_message.message_id
        date_str = db.reference(
            f"{cls.root}/users/{user.id}/message_date/{message_id}"
        ).get()
        if not isinstance(date_str, str):
            logging.debug(f"No upload date for message id {message_id} and user {user.id}.")
            return False
        today = datetime.date.fromisoformat(date_str)
        cls.publish(user, today, edited_message)
        return True

    @classmethod
    def set_user_timezone(cls, user: User, timezone: Union[datetime.tzinfo]) -> None:
        """
        Saves timezone for given user
        """
        db.reference(f"{cls.root}/users/{user.id}").update(
            {"timezone": timezone.__str__()}
        )

    @classmethod
    def get_user_timezone(cls, user: User) -> datetime.tzinfo:
        """
        Gets previously saved timezone for given user

        :param user: User whose timezone it is
        :return: timezone (if not previously saved, returns `UTC`)
        """
        tz_name = db.reference(f"{cls.root}/users/{user.id}/timezone").get()
        if tz_name is None:
            return pytz.UTC
        else:
            return pytz.timezone(tz_name)
