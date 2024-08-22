import os.path
import base64
import re
import os
import sys
import time
import datetime
import colorama
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import http.client, urllib

refreshTime = 5

reFindPattern = pattern = r"\$\d+(?:\.\d{2})?"
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.modify']
conn = http.client.HTTPSConnection("api.pushover.net:443")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def FormattedTime():
    currentTime = datetime.datetime.now().strftime("%H:%M:%S")
    currentTimeSplit = currentTime.split(":")

    timeEndToAdd = "AM"

    if currentTimeSplit[0] == "00":
        currentTimeSplit[0] = "12"

    elif int(currentTimeSplit[0]) >= 12:
        if int(currentTimeSplit[0]) > 12:
            currentTimeSplit[0] = str(int(currentTimeSplit[0]) - 12)
        timeEndToAdd = "PM"

    else:
        pass

    for num in range(0, len(currentTimeSplit) - 1):
        if len(currentTimeSplit[num]) == 1:
            currentTimeSplit[num] = "0" + currentTimeSplit[num]

    return f"[{currentTimeSplit[0]}:{currentTimeSplit[1]}:{currentTimeSplit[2]} {timeEndToAdd}]{colorama.Fore.RESET}"

def PreTimeLog():
    print(f"[¤¤:¤¤:¤¤ ¤¤]", end='', flush=True)

def TimeLog(message, col):
    print(f"\r{col}{FormattedTime()} {message}", flush=True)


def ReadEmails():
    #PreTimeLog()

    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(               
                # your creds file here. Please create json file as here https://cloud.google.com/docs/authentication/getting-started
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread Your ROI profit is available").execute()
        messages = results.get('messages',[]);
        if not messages:
            print(f'{colorama.Fore.LIGHTBLUE_EX}No New Email{colorama.Fore.RESET}')
        else:
            message_count = 0
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                email_data = msg['payload']['headers']
                for values in email_data:
                    name = values['name']
                    if name == 'From':
                        from_name= values['value']
                        try:
                            for part in msg['payload']['parts']:
                                try:
                                    data = part['body']["data"]
                                    byte_code = base64.urlsafe_b64decode(data)

                                    text = byte_code.decode("utf-8")

                                    amount = re.findall(pattern, text)[0]

                                    print(f"{colorama.Fore.GREEN}Updated ROI Profit: {amount}{colorama.Fore.RESET}")

                                    conn.request("POST", "/1/messages.json",
                                                 urllib.parse.urlencode({
                                                     "token": "ayvw5q9bw5jqhj4uy3hjjptfvxsktt",
                                                     "user": "uy8kizh369np8t6oihy9yhkfkgyn81",
                                                     "message": f"Updated ROI Profit: {amount}",
                                                 }), {"Content-type": "application/x-www-form-urlencoded"})

                                    r = conn.getresponse()
                                    r.read()

                                    # mark the message as read (optional)
                                    msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()

                                    time.sleep(refreshTime)
                                    ReadEmails()

                                except BaseException as error:
                                    pass
                        except KeyError:
                            try:
                                data = msg['payload']['body']["data"]
                                byte_code = base64.urlsafe_b64decode(data)

                                text = byte_code.decode("utf-8")

                                amount = re.findall(pattern, text)[0]

                                print(f"{colorama.Fore.GREEN}Updated ROI Profit: {amount}{colorama.Fore.RESET}")

                                conn.request("POST", "/1/messages.json",
                                            urllib.parse.urlencode({
                                                "token": "ayvw5q9bw5jqhj4uy3hjjptfvxsktt",
                                                "user": "uy8kizh369np8t6oihy9yhkfkgyn81",
                                                "message": f"Updated ROI Profit: {amount}",
                                            }), {"Content-type": "application/x-www-form-urlencoded"})

                                r = conn.getresponse()
                                r.read()

                                # mark the message as read (optional)
                                msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()

                                time.sleep(refreshTime)
                                ReadEmails()

                            except BaseException as error:
                               pass
    except Exception as error:
        print(f'{colorama.Fore.YELLOW}An error occurred: {error}{colorama.Fore.RESET}')

clear()

while True:
    ReadEmails()
    time.sleep(refreshTime)
