# birthday_reminder_notification
Reminds you of upcoming birthdays based on your Google Contacts list. It sends a pre-formatted message to your Telegram chat so you can just click on it and pre-fill over WhatsApp

## Requirements

1. Python 3.7+

2. Create Google OAuth2 [credentials](https://developers.google.com/identity/protocols/oauth2) using the `https://www.googleapis.com/auth/contacts.readonly` scope, and save the `credentials.json` file into the root of this project.

3. Telegram bot (create yours via [BotFather](https://t.me/botfather)). More info [here](https://core.telegram.org/bots#3-how-do-i-create-a-bot), and update the `config.yaml` file with your bot API key as well as your chat_id.

## Usage

1. Install the required libraries on a virtual enviroment (e.g. python3.7 -m pip install -r requirements.txt)

2. Edit `config.yaml` file with your Telegram Bot API key, your Name (so your contact can be ignored), and the `msg_settings` field with its related information - please remember to add the `{name}` variable into the message so it can be properly filled by the script.

3. Run `grab_contacts.py` (e.g. python3.7 grab_contacts.py). This will save your google contacts to a csv file (bday_detials.csv)

4. Set up a cron job to run `message.py` once a day. This file will check for existing birthdays on the day of, and if it detects any, will send you a message over Telegram. 