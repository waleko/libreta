import bot
import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
cache_dir = ".cache"


def main():
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)

    token = os.environ.get("TOKEN")
    fns_bot = bot.Bot(token)
    fns_bot.updater.start_polling()
    fns_bot.updater.idle()


if __name__ == "__main__":
    main()
