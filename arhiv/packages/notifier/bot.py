import os
from pathlib import Path
from telebot import TeleBot
from vyper import v

config = Path(__file__).parent.joinpath("../../").joinpath("config")
v.set_config_name("stg")
v.add_config_path(config)
v.read_in_config()


# class TelegramBot:
#     def __init__(self) -> None:
#
#         if chat_id := os.getenv('TELEGRAM_BOT_CHAT_ID'):
#             self._chat_id = int(chat_id)
#         else:
#             raise TelegramNotifierError('Need present environment variable "TELEGRAM_BOT_CHAT_ID"!')
#         if access_token := os.getenv('TELEGRAM_BOT_ACCESS_TOKEN'):
#             self._telegram_bot = TeleBot(access_token)
#         else:
#             raise TelegramNotifierError('Need present environment variable "TELEGRAM_BOT_ACCESS_TOKEN"!')


def send_file() -> None:
    telegram_bot = TeleBot(v.get("telegram.token"))
    file_path = Path(__file__).parent.joinpath("../../").joinpath("swagger-coverage-report.html")
    print("Looking for file at:", file_path)
    print("File exists:", os.path.exists(file_path))
    with open(file_path, "rb") as document:
        telegram_bot.send_document(
            v.get("telegram.chat_id"),
            document=document,
            caption="coverage",
        )


if __name__ == "__main__":
    send_file()
