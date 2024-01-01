from email.message import EmailMessage
import base64
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
import json

user_name = "Haley"
# Load environment variables from .env file
load_dotenv()

openai.api_key = os.environ.get("HALEYS_KEY")
SCOPES = ["https://mail.google.com/"]


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.8, 
    )
    return response.choices[0].message["content"]


def gmail_create_draft():
  """Create and insert a draft email.
   Print the returned draft's message and id.
   Returns: Draft object, including draft id and message meta data.

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
  creds = main()

  try:
    # create gmail api client
    service = build("gmail", "v1", credentials=creds)

    message = EmailMessage()

    message.set_content("This is automated draft mail")

    message["To"] = "2022hachen@gmail.com"
    message["From"] = "2022hachen@gmail.com"
    message["Subject"] = "Automated draft"

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"message": {"raw": encoded_message}}
    # pylint: disable=E1101
    draft = (
        service.users()
        .drafts()
        .create(userId="me", body=create_message)
        .execute()
    )

    print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')

  except HttpError as error:
    print(f"An error occurred: {error}")
    draft = None

  sendyn = (input("Here's your draft. Send? (Y/N) /n" + message.get_content()) == "y")
  if sendyn:
    send_draft(service, "me", draft["id"])
  return draft

# If modifying these scopes, delete the file token.json.
def send_draft(service, user_id, draft_id):
    """Send an email draft."""
    try:
        # pylint: disable=E1101
        service.users().drafts().send(userId=user_id, body={"id": draft_id}).execute()

        print(f"Draft sent! Draft Id: {draft_id}")
    except HttpError as error:
        print(f"An error occurred while sending the draft: {error}")

def search_messages(query):
    creds = main()

    try:
        service = build("gmail", "v1", credentials=creds)
        # Use the users().messages().list method with the 'q' parameter for searching
        response = service.users().messages().list(userId="me", q=query).execute()
        messages = response.get('messages', [])

        if not messages:
            print(f"No messages found for the query: {query}")
            return []

        print(f"Messages found for the query '{query}':")
        for message in messages:
            message_id = message['id']
            message_details = service.users().messages().get(userId="me", id=message_id).execute()
            subject = next((header['value'] for header in message_details['payload']['headers'] if header['name'] == 'Subject'), 'N/A')
            print(f"Message ID: {message_id}, Subject: {subject}")

        return messages

    except Exception as error:
        print(f"An error occurred while searching messages: {error}")
        return []

def add_label_to_message(message_id, label_name):
    creds = main()

    try:
        service = build("gmail", "v1", credentials=creds)
        # Use the users().messages().modify method to add labels to the message
        #create_label(service, label_name)
        label_id = ""
        labels = service.users().labels().list(userId="me").execute().get("labels", [])
        for label in labels:
            if label["name"] == label_name:
                 label_id = label["id"]

        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"addLabelIds": [label_id], "removeLabelIds": []},
        ).execute()

        print(f"Label '{label_name}' added to message ID: {message_id}")
    except HttpError as error:
        print(f"An error occurred while adding label to the message: {error}")

def create_label(service, label_name):
    try:
        # Use the users().labels().create method to create a new label
        label = service.users().labels().create(
            userId="me",
            body={"name": label_name, "labelListVisibility": "labelShow", "messageListVisibility": "show"},
        ).execute()

        print(f"Label '{label_name}' created with ID: {label['id']}")
        return label['id']
    except HttpError as error:
        print(f"An error occurred while creating the label: {error}")
        return None

def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])

    """
    if not labels: 
      print("No labels found.")
      return
    print("Labels:")
    for label in labels:
      print(label["name"])
    """
  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")
    
  return creds


if __name__ == "__main__":
  gmail_create_draft()
  """
  search_query = "automated draft"  # Replace with the keyword you want to search for
  label_name = "Automated"
  add_label_to_message("18cc26ef19c6601f", label_name)
  """


 
