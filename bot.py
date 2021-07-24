from telegram.ext import Updater

import handlers.handlers


class Bot:
    def __init__(self, token):
        self.updater = Updater(token)
        for handler in handlers.handlers:
            self.updater.dispatcher.add_handler(handler)
