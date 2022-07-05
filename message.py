import csv
import datetime
import logging
import urllib.parse
from pathlib import Path

import yaml
from phone_iso3166.country import phone_country
from telegram import Bot, ParseMode

FILE_SOURCE = Path(__file__).parent / "bday_details.csv"
FILE_YAML = Path(__file__).parent / "config.yaml"
YAML_RULES = yaml.load(open(FILE_YAML, "r"), Loader=yaml.FullLoader)
TELEGRAM = Bot(token=YAML_RULES["config"][0]["bot_token"])
TELEGRAM_CHAT_ID = YAML_RULES["config"][0]["chat_id"]


def check_birthday(today):
    """
    This function will check if there are any birthdays today
    """

    birthdays = []
    with open(FILE_SOURCE, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["birthday"] == today:
                birthdays.append(row)
    csvfile.close()
    return birthdays


def send_message(birthday_list):
    """
    This function will build the message and send it to Telegram
    """
    msg_settings = YAML_RULES["msg_settings"]
    for item in birthday_list:
        phone_number = item["phoneNumber"][2:-2]
        msg_intro = (
            f"It's <b>{item['displayName']}'s</b> birthday! "
            "Click on the link to send them a message "
            f"https://wa.me/{phone_number}?text="
        )
        country = phone_country(int(phone_number))

        for i in range(len(msg_settings)):
            if country in msg_settings[i]["country"]:
                msg_bday = msg_settings[i]["msg"].format(name=item["givenName"])
                final_msg = f"{msg_intro}{urllib.parse.quote(msg_bday)}"
                logging.info(
                    f"Sending Bday MSG to: {item['displayName']} in {msg_settings[i]['language']}"
                )
                TELEGRAM.send_message(
                    TELEGRAM_CHAT_ID,
                    final_msg,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )


def main():
    """
    This function will grab today's date and if there are any birthdays today,
     it will send a telegram message to the `TELEGRAM_CHAT_ID`
     with a whatsapp link that you can click to have the message pre-filled.
    """

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logging.info(f"Starting...")

    # format MM/DD based on `grab_contacts.py`
    today = datetime.datetime.now().strftime("%m/%d")
    logging.info(f"Today's date: {today}")

    birthday_list = check_birthday(today)
    logging.info(f"Birthdays today: {len(birthday_list)}")

    # if there are birthdays today, continue
    if birthday_list:
        send_message(birthday_list)
    logging.info(f"Exiting...")
    return


if __name__ == "__main__":

    main()
