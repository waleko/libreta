from typing import List

from telegram.ext import Handler

handlers: List[Handler] = []


def register_handler(handler: Handler):
    handlers.append(handler)
