import os
import base64
import logging
from typing import List, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime

from .database import get_connection

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')

def get_credentials() -> Credentials:
    """Gets valid user credentials from storage or initiates OAuth flow."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                logger.info("\n=== Google Calendar Setup Required ===")
                logger.info("To enable Google Calendar syncing, you need OAuth credentials.")
                logger.info("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
                logger.info("2. Create a Project and enable the 'Google Calendar API'.")
                logger.info("3. Create an 'OAuth client ID' (Application type: Desktop app).")
                logger.info("4. Download the JSON file, name it 'credentials.json', and place it in the ContestPilot folder.")
                logger.info("======================================\n")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            
    return creds

def make_stable_event_id(contest_id: str) -> str:
    """
    Google Calendar event IDs must be base32hex encoded without padding.
    Allowed chars: a-v and 0-9.
    """
    # Use base64 b32hexencode which maps to 0-9 and A-V
    encoded_bytes = base64.b32hexencode(contest_id.encode('utf-8'))
    return encoded_bytes.decode('utf-8').lower().replace('=', '')

def build_event_body(contest: dict) -> dict:
    """Builds the Google Calendar event dictionary."""
    priority = contest['priority'].upper()
    reason = contest['reason']
    
    summary = f"[{priority}] {contest['name']}"
    if contest.get('status') == 'CANCELED':
        summary = f"[CANCELED] {contest['name']}"
    
    event = {
        'id': make_stable_event_id(contest['id']),
        'summary': summary,
        'description': f"Platform: {contest['platform'].title()}\nPriority: {priority}\nReason: {reason}\nURL: {contest['url']}",
        'start': {
            'dateTime': contest['start_time'],
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': contest['end_time'],
            'timeZone': 'UTC',
        },
        'reminders': {
            'useDefault': False,
            'overrides': []
        }
    }
    
    if contest.get('status') == 'CANCELED':
        # Leave overrides empty for canceled events
        pass
    else:
        # Smart Reminders based on priority
        if priority == 'HIGH':
            event['reminders']['overrides'] = [
                {'method': 'popup', 'minutes': 24 * 60}, # 24 hours before
                {'method': 'popup', 'minutes': 60},      # 1 hour before
            ]
        elif priority == 'MEDIUM':
            event['reminders']['overrides'] = [
                {'method': 'popup', 'minutes': 60},      # 1 hour before
            ]
        # If LOW, overrides remain empty (no popups), but it's still visible on the calendar!
    
    return event

def get_upcoming_contests_with_rankings() -> List[dict]:
    """Fetches upcoming contests from DB with their rankings."""
    conn = get_connection()
    cursor = conn.cursor()
    # Filter for contests that haven't ended yet
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    query = '''
        SELECT c.*, r.priority, r.reason 
        FROM contests c
        LEFT JOIN rankings r ON c.id = r.contest_id
        WHERE c.end_time > ?
    '''
    rows = cursor.execute(query, (now_iso,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def sync_calendar():
    """Main sync function to push events to Google Calendar."""
    creds = get_credentials()
    if not creds:
        return
        
    service = build('calendar', 'v3', credentials=creds)
    contests = get_upcoming_contests_with_rankings()
    
    logger.info(f"Syncing {len(contests)} contests to Google Calendar...")
    synced_count = 0
    
    for contest in contests:
        if not contest.get('priority'):
            # Fallback if unranked
            contest['priority'] = 'MEDIUM'
            contest['reason'] = 'Unranked default'
            
        event_body = build_event_body(contest)
        event_id = event_body['id']
        
        try:
            # Try to insert
            service.events().insert(calendarId='primary', body=event_body).execute()
            synced_count += 1
        except HttpError as e:
            if e.resp.status == 409:
                # 409 Conflict: Event already exists, let's update it!
                try:
                    service.events().update(calendarId='primary', eventId=event_id, body=event_body).execute()
                    synced_count += 1
                except HttpError as update_e:
                    logger.error(f"Failed to update event {contest['name']}: {update_e}")
            else:
                logger.error(f"Failed to insert event {contest['name']}: {e}")
                
    logger.info(f"Calendar sync complete! Successfully pushed {synced_count} events.")
