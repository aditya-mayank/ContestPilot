import sqlite3
import os
import logging
from typing import List, Optional
from .models import Contest, UserPreference, SyncState, ReminderHistory

logger = logging.getLogger(__name__)

# To make this idempotent, we will store the DB in the root app directory
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'contestpilot.db')

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def is_initialized() -> bool:
    """Check if the database has been initialized."""
    if not os.path.exists(DB_PATH):
        return False
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='preferences'")
        initialized = cursor.fetchone() is not None
        conn.close()
        return initialized
    except Exception:
        return False

def init_db():
    """Initializes the database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contests (
            id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            name TEXT NOT NULL,
            platform TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration_seconds INTEGER,
            url TEXT,
            status TEXT,
            calendar_event_id TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sync_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_cache (
            url TEXT PRIMARY KEY,
            response TEXT NOT NULL,
            fetched_at TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            contest_id TEXT,
            reminder_type TEXT,
            sent_at TEXT,
            PRIMARY KEY (contest_id, reminder_type)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rankings (
            contest_id TEXT PRIMARY KEY,
            priority TEXT NOT NULL,
            reason TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            contest_id TEXT NOT NULL,
            message TEXT,
            created_at TEXT NOT NULL,
            sent INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contest_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contest_id TEXT NOT NULL,
            change_type TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            changed_at TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contest_id TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sync_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sync_time TEXT NOT NULL,
            contests_fetched INTEGER,
            new_added INTEGER,
            updated INTEGER,
            canceled INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            sent_at TEXT NOT NULL,
            details TEXT
        )
    ''')

    conn.commit()
    conn.close()
    logger.debug("Database initialized.")

# --- Notifications ---
def queue_notification(notif_type: str, contest_id: str, message: str):
    conn = get_connection()
    cursor = conn.cursor()
    from .utils import utc_now_iso
    cursor.execute('''
        INSERT INTO notifications_queue (type, contest_id, message, created_at)
        VALUES (?, ?, ?, ?)
    ''', (notif_type, contest_id, message, utc_now_iso()))
    conn.commit()
    conn.close()

def get_pending_notifications() -> List[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute('SELECT * FROM notifications_queue WHERE sent = 0 ORDER BY created_at ASC').fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_notification_sent(notif_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE notifications_queue SET sent = 1 WHERE id = ?', (notif_id,))
    conn.commit()
    conn.close()

# --- History ---
def log_history(contest_id: str, change_type: str, old_value: str, new_value: str):
    conn = get_connection()
    cursor = conn.cursor()
    from .utils import utc_now_iso
    cursor.execute('''
        INSERT INTO contest_history (contest_id, change_type, old_value, new_value, changed_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (contest_id, change_type, old_value, new_value, utc_now_iso()))
    conn.commit()
    conn.close()

# --- Contests ---
def save_contest(contest: Contest):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if contest exists to detect changes
    cursor.execute('SELECT name, start_time FROM contests WHERE id = ?', (contest.id,))
    row = cursor.fetchone()
    
    # Format the time nicely
    import datetime
    from tzlocal import get_localzone
    try:
        start_dt = datetime.datetime.fromisoformat(contest.start_time.replace('Z', '+00:00'))
        local_tz = get_localzone()
        start_local = start_dt.astimezone(local_tz).strftime('%b %d, %I:%M %p')
    except Exception:
        start_local = contest.start_time

    if not row:
        msg = f"New contest added: {contest.name}\nPlatform: {contest.platform.title()}\nTime: {start_local}\nLink: {contest.url}"
        queue_notification('ADDED', contest.id, msg)
    else:
        if row['start_time'] != contest.start_time:
            log_history(contest.id, 'TIME', row['start_time'], contest.start_time)
            msg = f"Contest time updated: {contest.name}\nPlatform: {contest.platform.title()}\nNew Time: {start_local}\nLink: {contest.url}"
            queue_notification('UPDATED', contest.id, msg)
        if row['name'] != contest.name:
            log_history(contest.id, 'TITLE', row['name'], contest.name)
            msg = f"Contest title changed: from '{row['name']}' to '{contest.name}'\nPlatform: {contest.platform.title()}\nTime: {start_local}\nLink: {contest.url}"
            queue_notification('UPDATED', contest.id, msg)
        
    cursor.execute('''
        INSERT INTO contests (id, source_id, name, platform, start_time, end_time, duration_seconds, url, status, calendar_event_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            start_time=excluded.start_time,
            end_time=excluded.end_time,
            duration_seconds=excluded.duration_seconds,
            url=excluded.url,
            status=excluded.status,
            calendar_event_id=COALESCE(excluded.calendar_event_id, contests.calendar_event_id)
    ''', (
        contest.id, contest.source_id, contest.name, contest.platform, contest.start_time, 
        contest.end_time, contest.duration_seconds, contest.url, 
        contest.status, contest.calendar_event_id
    ))
    conn.commit()
    conn.close()

# --- Preferences ---
def set_preference(key: str, value: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO preferences (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value', (key, value))
    conn.commit()
    conn.close()

def get_preference(key: str) -> Optional[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM preferences WHERE key = ?', (key,))
    row = cursor.fetchone()
    conn.close()
    return row['value'] if row else None

# --- Cache ---
def get_api_cache(url: str) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT response, fetched_at FROM api_cache WHERE url = ?', (url,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'response': row['response'], 'fetched_at': row['fetched_at']}
    return None

def set_api_cache(url: str, response: str, fetched_at: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO api_cache (url, response, fetched_at)
        VALUES (?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
            response=excluded.response,
            fetched_at=excluded.fetched_at
    ''', (url, response, fetched_at))
    conn.commit()
    conn.close()

# --- Rankings ---
def save_ranking(contest_id: str, priority: str, reason: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO rankings (contest_id, priority, reason)
        VALUES (?, ?, ?)
        ON CONFLICT(contest_id) DO UPDATE SET
            priority=excluded.priority,
            reason=excluded.reason
    ''', (contest_id, priority, reason))
    conn.commit()
    conn.close()

def get_ranking(contest_id: str) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT priority, reason FROM rankings WHERE contest_id = ?', (contest_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'priority': row['priority'], 'reason': row['reason']}
    return None
