"""
  taken from 
  https://developers.google.com/calendar/api/quickstart/python
  https://developers.google.com/calendar/api/v3/reference/events/list
  see this too
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
import pytz
import argparse

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'. Expected format YYYY-MM-DD.".format(s)
        raise argparse.ArgumentTypeError(msg)

def get_args():
    parser = argparse.ArgumentParser(description="Process a date.")
    parser.add_argument("date", help="The date in YYYY-MM-DD format", type=valid_date)
    args = parser.parse_args()
    return args


def get_events_by_date(api_service, event_date):
    """ Does return some spurious events beyond the ask, need to understand this better"""
    split_date = event_date.split('-')

    event_date_dt = datetime(int(split_date[0]), int(split_date[1]), int(split_date[2]), 0, 00, 00, 0)
    
    event_date = pytz.UTC.localize(event_date_dt).isoformat()

    end = datetime(int(split_date[0]), int(split_date[1]), int(split_date[2]), 23, 59, 59, 999999)
    end = pytz.UTC.localize(end).isoformat()
    
    events_result = api_service.events().list(calendarId='primary', 
                                              timeMin=event_date, 
                                              timeMax=end,
                                              singleEvents=True,
                                              orderBy="startTime",
                                              timeZone="America/Los_Angeles").execute()
    return event_date, events_result.get('items', [])
    
def strip_time_from_date(date_str):
  return date_str.split('T')[0]

def main():
  """ Uses the Google Calendar API
      Send to ChatGPT to write a nice exec summary
  """
  
  args = get_args()
  date = args.date
  print(f'type of date: {type(args.date)}')
  print("Validated date:", date.strftime("%Y-%m-%d"))
  date_str = date.strftime("%Y-%m-%d")
    
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
    event_date_str, all_events = get_events_by_date(service, date_str)
    event_date_str = strip_time_from_date(event_date_str)
    
    print(f'LotD for {event_date_str}')
    for event in all_events:
      
      start = event["start"].get("dateTime", event["start"].get("date"))
      if "date" in event["start"]:
        date_str = event["start"]["date"]
      elif "dateTime" in event["start"]:
        date_str = event["start"]["dateTime"]
      time_striped_date = strip_time_from_date(date_str)
      
      # print(f'++ extracted date str: {time_striped_date}')
      
      end = event["end"].get("dateTime", event["end"].get("date"))
      
      if (event_date_str == time_striped_date) and not((event["summary"] == "Home") or (event["summary"]=="schedule my day")):
        print(f'start: {start}, end: {end}, Summary: {event["summary"]}')
      
        if "description" in event:
          print(event["description"])
      
    

  except HttpError as error:
    print(f"An error occurred: {error}")

    
if __name__ == "__main__":
  main()
