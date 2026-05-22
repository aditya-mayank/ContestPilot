from googleapiclient.discovery import build
from contestpilot.calendar_sync import get_credentials

def flush_all():
    print("Flushing ALL ContestPilot events from Google Calendar...")
    creds = get_credentials()
    if not creds:
        return
        
    service = build('calendar', 'v3', credentials=creds)
    
    page_token = None
    deleted = 0
    while True:
        events_result = service.events().list(calendarId='primary', pageToken=page_token).execute()
        events = events_result.get('items', [])
        
        for event in events:
            desc = event.get('description', '')
            # Our events always have "Platform: " and "URL: " in the description
            if desc and 'Platform:' in desc and 'URL:' in desc:
                try:
                    service.events().delete(calendarId='primary', eventId=event['id']).execute()
                    deleted += 1
                    print(f"Deleted: {event.get('summary')}")
                except Exception as e:
                    print(f"Error deleting {event['id']}: {e}")
        
        page_token = events_result.get('nextPageToken')
        if not page_token:
            break
            
    print(f"\n✅ Flush complete. Deleted {deleted} legacy events from Google Calendar.")

if __name__ == '__main__':
    flush_all()
