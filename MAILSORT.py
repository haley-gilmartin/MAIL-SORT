from email.message import EmailMessage
import base64
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os.path
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import openai
from openai import OpenAI
client = OpenAI(
    api_key=os.environ.get("MAIL-SORT-KEY"),
)
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
import json

import pandas as pd
import numpy as np
#from ast import literal_eval
#from openai import cosine_similarity



user_name = "Admin"
# Load environment variables from .env file
load_dotenv()

openai.api_key = os.environ.get("MAIL-SORT-KEY")
SCOPES = ["https://mail.google.com/"]


## there are several ways to do this for some reason. see other doc
def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.8, 
    )
    return response.choices[0].message["content"]

## Pandas feed
try: 
  df = pd.read_csv('user_message_vector_data.csv')

  """ found this online. not terribly sure what it does
  try: 
     df["embedding"] = df.embedding.apply(literal_eval).apply(np.array)
  except Exception as error:
     embed_user_data()
  """
except Exception as error:
  df = pd.DataFrame(columns=['content', 'embedding'])

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding




# search function using vector embeddings
# this takes way too long. It makes a call for each message. we need to make it so we store the vectors first,
# then apply similarity scoring.
# thinking cosine similarity algorithm?
##### REPLACE
def vector_search(query, data_frame):
    # calculate similarity score
    similarity_scores = data_frame['content'].apply(lambda msg: get_completion(query + " " + msg))

    # Get the index of the message with the highest similarity score
    max_similarity_index = similarity_scores.idxmax()

    # Return the message content
    return data_frame.loc[max_similarity_index, 'content']


# Writes user data to a .csv file
# needs further specificity and illustration <--- WHEN YOU UPDATE THIS, UPDATE THE INITIALIZATION OF DF
def add_message_to_user_data(message, csv_file='user_message_vector_data.csv'):
    # Check if the CSV file exists
    if os.path.exists(csv_file):
        # If it exists, load the existing DataFrame
        df = pd.read_csv(csv_file)
    else:
        # If it doesn't exist, create a new DataFrame
        df = pd.DataFrame(columns=['content', 'embedding'])

    # Append the new message to the DataFrame
    df.loc[len(df.index)] = [message, get_embedding(message, model='text-embedding-ada-002')] 

    # Write the DataFrame back to the CSV file
    df.to_csv(csv_file, index=False)

def embed_user_data():
   #format existing emails into a .csv file and add an "embedding" column
   # https://cookbook.openai.com/examples/semantic_text_search_using_embeddings
   return ""

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
    message["From"] = "2022hachen@gmail.com"  # <--- somehow, this is overwritten in  OAuth
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
  print(get_embedding("hello my name is haley"))



 
