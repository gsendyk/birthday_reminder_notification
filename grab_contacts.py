import csv
import logging
import os.path
from collections import defaultdict
from pathlib import Path

import yaml
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

FILE_YAML = Path(__file__).parent / "config.yaml"
YAML_RULES = yaml.load(open(FILE_YAML, "r"), Loader=yaml.FullLoader)

SCOPES = ["https://www.googleapis.com/auth/contacts.readonly"]


def login_google():
    """
    Logs into Google and save credentials
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def retrive_contacts(creds):
    """
    Will retrieve up to 1k contacts names, phone numbers and birthdays
    https://developers.google.com/people/api/rest/v1/people.connections/list
    """
    try:
        service = build("people", "v1", credentials=creds)
        results = (
            service.people()
            .connections()
            .list(
                resourceName="people/me",
                pageSize=1000,
                personFields="names,phoneNumbers,birthdays",
            )
            .execute()
        )
        connections = results.get("connections", [])
        return connections
    except HttpError as err:
        logging.exception(err)
        return False


def prep_dict(contacts_list):
    """
    This will prepare a dict list to be able to save on a csv file
    """

    try:
        data = defaultdict(list)
        for person in contacts_list:
            birthday = person.get("birthdays", [])
            if birthday:
                if person["names"][0]["displayName"].title() != YAML_RULES["google"]["your_name"]:
                    date = person["birthdays"][0]["date"]
                    month = f"{date['month']:02}"
                    day = f"{date['day']:02}"
                    number = [
                        number["canonicalForm"].replace("+", "")
                        for number in person["phoneNumbers"]
                        if number["type"] == "mobile"
                    ]

                    data["displayName"].append(person["names"][0]["displayName"].title())
                    data["givenName"].append(person["names"][0]["givenName"].title())
                    data["phoneNumber"].append(number)
                    data["birthday"].append(f"{month}/{day}")

        return data

    except Exception as e:
        logging.exception(e)
        return False


def main():
    """
    This runs the main program that pulls your contact
     list with birthdays and saves it on a csv file.
    """

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logging.info("Starting...")

    logging.info("Trying to log into Google...")
    login = login_google()

    logging.info("Trying to retrieve contacts...")
    contacts_list = retrive_contacts(login)

    if contacts_list:
        prep_data = prep_dict(contacts_list)

        if prep_data:
            logging.info(f"Trying to save output to a csv file...")
            final_data = zip(*prep_data.values())
            with open("bday_details.csv", "w", newline="") as f:
                csv_output = csv.writer(f)
                csv_output.writerow(list(prep_data.keys()))
                csv_output.writerows(final_data)

            f.close()
            logging.info(f"Saved")

    logging.info(f"Exiting...")


if __name__ == "__main__":
    main()
