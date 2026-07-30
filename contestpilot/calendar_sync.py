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
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            logger.warning(f"Could not load stored token: {e}")
            creds = None
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Google OAuth refresh token expired or invalid ({e}). Requesting re-authorization...")
                if os.path.exists(TOKEN_FILE):
                    try:
                        os.remove(TOKEN_FILE)
                    except OSError:
                        pass
                creds = None

        if not creds or not creds.valid:
            if not os.path.exists(CREDENTIALS_FILE):
                logger.info("\n=== Google Calendar Setup Required ===")
                logger.info("To enable Google Calendar syncing, you need OAuth credentials.")
                logger.info("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
                logger.info("2. Create a Project and enable the 'Google Calendar API'.")
                logger.info("3. Create an 'OAuth client ID' (Application type: Desktop app).")
                logger.info("4. Download the JSON file, name it 'credentials.json', and place it in the ContestPilot folder.")
                logger.info("======================================\n")
                return None
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                logger.error(f"OAuth authorization flow failed: {e}")
                return None
        
        # Save the credentials for the next run
        if creds:
            try:
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                logger.error(f"Could not save token file: {e}")
            
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
        'status': 'confirmed',
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
        elif priority in ['MEDIUM', 'LOW']:
            event['reminders']['overrides'] = [
                {'method': 'popup', 'minutes': 60},      # 1 hour before
            ]
    
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
    try:
        creds = get_credentials()
    except Exception as e:
        logger.error(f"Failed to obtain calendar credentials: {e}")
        return

    if not creds:
        return
        
    try:
        service = build('calendar', 'v3', credentials=creds)
        contests = get_upcoming_contests_with_rankings()
    except Exception as e:
        logger.error(f"Failed to initialize calendar service or fetch contests: {e}")
        return
    
    print(f" 📅 Pushing {len(contests)} contests to Google Calendar...")
    synced_count = 0
    
    for contest in contests:
        if not contest.get('priority'):
            # Fallback if unranked
            contest['priority'] = 'MEDIUM'
            contest['reason'] = 'Unranked default'
            
        event_body = build_event_body(contest)
        try:
            service.events().insert(calendarId='primary', body=event_body).execute()
            synced_count += 1
        except Exception as e:
            if '409' in str(e):
                # 409 Conflict: Event ID already exists (active or cancelled ghost).
                # update() with status:'confirmed' will restore it to visible.
                try:
                    service.events().update(calendarId='primary', eventId=event_body['id'], body=event_body).execute()
                    synced_count += 1
                except Exception:
                    pass
            else:
                pass  # Silently skip other errors

    print(f" ✅ Calendar sync complete! ({synced_count} events updated)")

def clear_all_contests():
    """Hunts down and deletes all ContestPilot events from Google Calendar."""
    try:
        creds = get_credentials()
    except Exception as e:
        logger.error(f"Failed to obtain calendar credentials: {e}")
        return

    if not creds:
        print(" [Error] Cannot access Calendar. No credentials found.")
        return
        
    service = build('calendar', 'v3', credentials=creds)
    print(" 🧹 Scanning your Google Calendar for ContestPilot events...")
    
    deleted_count = 0
    page_token = None
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    while True:
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            singleEvents=True, orderBy='startTime', pageToken=page_token).execute()
        events = events_result.get('items', [])
        
        for event in events:
            # ContestPilot events have specific formatting in their descriptions
            desc = event.get('description', '')
            if 'Platform:' in desc and 'Priority:' in desc and 'URL:' in desc:
                eid = event.get('id', '')
                try:
                    service.events().delete(calendarId='primary', eventId=eid).execute()
                    deleted_count += 1
                    print(f"   🗑️  Deleted: {event.get('summary')}")
                except Exception as e:
                    pass
        
        page_token = events_result.get('nextPageToken')
        if not page_token:
            break
            
    print(f"\n ✅ Cleanup Complete! Removed {deleted_count} ContestPilot events from your calendar.")
