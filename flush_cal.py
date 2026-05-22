import sqlite3
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from contestpilot.calendar_sync import get_credentials, make_stable_event_id

def flush_calendar():
    print("Flushing Google Calendar events...")
    creds = get_credentials()
    if not creds:
        print("No credentials found!")
        return
        
    service = build('calendar', 'v3', credentials=creds)
    
    conn = sqlite3.connect('contestpilot.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all contests
    rows = cursor.execute('SELECT id FROM contests').fetchall()
    
    deleted = 0
    for row in rows:
        event_id = make_stable_event_id(row['id'])
        try:
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            deleted += 1
            print(f"Deleted event: {event_id}")
        except HttpError as e:
            if e.resp.status != 404: # Ignore 404s (already deleted)
                print(f"Error deleting {event_id}: {e}")
                
    cursor.execute("UPDATE contests SET calendar_event_id = NULL")
    conn.commit()
    conn.close()
    
    print(f"\nFlush complete. Deleted {deleted} events from Google Calendar.")

if __name__ == '__main__':
    flush_calendar()
