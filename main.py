import base64
import json

import bot
import os
import logging

from firebase import FirebaseUtils

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
cache_dir = ".cache"


def main():
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)

    credentials = json.loads(base64.b64decode(os.environ.get("FIREBASE_SVC_ACCOUNT")))
    databaseURL = os.environ.get("databaseURL")
    FirebaseUtils.setup_firebase(credentials, databaseURL)

    token = os.environ.get("TOKEN")
    fns_bot = bot.Bot(token)
    fns_bot.updater.start_polling()
    fns_bot.updater.idle()


if __name__ == "__main__":
    main()
