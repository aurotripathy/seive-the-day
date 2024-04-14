"""
  taken from 
  https://developers.google.com/calendar/api/quickstart/python
  and modified
  see this
  https://stackoverflow.com/questions/73822462/how-to-return-all-events-on-a-specific-date-in-google-calendar-api
"""
import datetime 
from datetime import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

import pytz

def get_events_by_date(api_service, event_date):

    split_date = event_date.split('-')

    event_date = datetime(int(split_date[0]), int(split_date[1]), int(split_date[2]), 6, 00, 00, 0)
    event_date = pytz.UTC.localize(event_date).isoformat()

    end = datetime(int(split_date[0]), int(split_date[1]), int(split_date[2]), 23, 59, 59, 999999)
    end = pytz.UTC.localize(end).isoformat()

    # events_result = api_service.events().list(calendarId='primary', timeMin=event_date,timeMax=end).execute()
    events_result = api_service.events().list(calendarId='primary', timeMin=event_date,timeMax=end, timeZone="UTC").execute()
    return events_result.get('items', [])


def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
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
    service = build("calendar", "v3", credentials=creds)
    all_events = get_events_by_date(service, "2024-4-12")
    
    for event in all_events:
        print(event['summary'])
    
    # Call the Calendar API
    now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    # now = datetime.datetime(year=24, month=4, day=12, hour=6, minute=0, second=0).isoformat() + "Z"
    # time_min = datetime.datetime(year=24, month=4, day=12, hour=6, minute=0, second=0).isoformat() + "Z"
    # time_max = datetime.datetime(year=24, month=4, day=12, hour=20, minute=0, second=0).isoformat() + "Z"
    # print(f'time min: {time_min} type: {type(time_min)}')
    # print(f'time max: {time_max}')
    
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            singleEvents=True,
            maxResults=10,
            orderBy="startTime",
            timeZone="America/Los_Angeles",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      end = event["end"].get("dateTime", event["end"].get("date"))
      print(start, end, event["summary"])

    

  except HttpError as error:
    print(f"An error occurred: {error}")

  # # new one
  # try:
  #     service = build("calendar", "v3", credentials=creds)
  #     event= {
  #       'start': {
  #         'dateTime': '2024-05-28T09:00:00-07:00',
  #         'timeZone': 'America/Los_Angeles',
  #       },
  #       'end': {
  #         'dateTime': '2024-05-28T17:00:00-07:00',
  #         'timeZone': 'America/Los_Angeles',
  #       },
  #     }

  #     event_results = (
  #       service.events()
  #       .list(
  #         calendarId='primary', 
  #         body=event)
  #       .execute()
  #     )
  #     events = event_results.get("items", [])
    
  # except HttpError as error:
  #     print(f"An error occurred: {error}")
    
if __name__ == "__main__":
  main()
