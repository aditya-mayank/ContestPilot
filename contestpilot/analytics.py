import logging
import datetime
from typing import List, Dict, Any
from .database import get_connection
from .utils import utc_now_iso

logger = logging.getLogger(__name__)

def log_sync(fetched: int, added: int, updated: int, canceled: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sync_history (sync_time, contests_fetched, new_added, updated, canceled)
        VALUES (?, ?, ?, ?, ?)
    ''', (utc_now_iso(), fetched, added, updated, canceled))
    conn.commit()
    conn.close()

def mark_attendance(search_term: str, action: str):
    """Fuzzy searches for a contest and marks it ATTENDED or SKIPPED."""
    action = action.upper()
    if action not in ('ATTENDED', 'SKIPPED'):
        logger.error("Invalid action. Use ATTENDED or SKIPPED.")
        return
        
    conn = get_connection()
    cursor = conn.cursor()
    
    # Search by ID or Name
    query = "SELECT id, name, platform, start_time FROM contests WHERE id LIKE ? OR name LIKE ? ORDER BY start_time DESC LIMIT 5"
    term = f"%{search_term}%"
    rows = cursor.execute(query, (term, term)).fetchall()
    
    if not rows:
        print(f"[Error] No contests found matching '{search_term}'.")
        conn.close()
        return
        
    if len(rows) > 1:
        print(f"[Warning] Multiple contests found for '{search_term}'. Please be more specific.")
        for i, r in enumerate(rows):
            print(f"  {i+1}. [{r['platform']}] {r['name']} ({r['start_time'][:10]}) - ID: {r['id']}")
        conn.close()
        return
        
    contest = rows[0]
    cid = contest['id']
    
    # Insert or replace action
    cursor.execute('''
        INSERT INTO user_actions (contest_id, action, timestamp)
        VALUES (?, ?, ?)
    ''', (cid, action, utc_now_iso()))
    
    conn.commit()
    conn.close()
    
    print(f"[Success] Marked '{contest['name']}' as {action}!")

def get_unreviewed_finished_contests() -> List[dict]:
    """Gets contests that have finished but have no action logged."""
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    query = '''
        SELECT c.* 
        FROM contests c
        LEFT JOIN user_actions u ON c.id = u.contest_id
        WHERE c.end_time < ? 
          AND c.status != 'CANCELED'
          AND u.id IS NULL
        ORDER BY c.end_time DESC
        LIMIT 10
    '''
    rows = cursor.execute(query, (now_iso,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def interactive_review():
    """CLI prompt to quickly review past contests."""
    unreviewed = get_unreviewed_finished_contests()
    if not unreviewed:
        print("You are all caught up! No recent unreviewed contests.")
        return
        
    print(f"Found {len(unreviewed)} unreviewed contests that have ended.")
    print("Type 'y' for attended, 'n' for skipped, 's' to skip reviewing for now.")
    print("-" * 40)
    
    for contest in unreviewed:
        ans = input(f"Did you attend [{contest['platform']}] {contest['name']}? (Y/N/S): ").strip().lower()
        if ans == 'y':
            mark_attendance(contest['id'], 'ATTENDED')
        elif ans == 'n':
            mark_attendance(contest['id'], 'SKIPPED')
        elif ans == 's':
            continue
        else:
            print("Invalid input, skipping...")

def get_streak() -> int:
    """Calculates consecutive weeks with at least one ATTENDED contest."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # We look at weeks where action = 'ATTENDED'
    query = '''
        SELECT DISTINCT strftime('%Y-%W', timestamp) as week_str
        FROM user_actions
        WHERE action = 'ATTENDED'
        ORDER BY week_str DESC
    '''
    rows = cursor.execute(query).fetchall()
    conn.close()
    
    if not rows:
        return 0
        
    # Python strftime('%W') counts Monday as first day of week.
    # To calculate continuous streak, we parse the year and week numbers.
    current_year, current_week = datetime.datetime.now().isocalendar()[:2]
    
    streak = 0
    expected_week = current_week
    expected_year = current_year
    
    for row in rows:
        y, w = map(int, row['week_str'].split('-'))
        
        if y == expected_year and w == expected_week:
            streak += 1
            # Decrement week
            expected_week -= 1
            if expected_week <= 0:
                expected_year -= 1
                # ISO weeks in a year can be 52 or 53, approximation to 52 for simplicity in backward tracking
                expected_week = 52 
        elif y == current_year and w == current_week - 1 and streak == 0:
            # If they haven't attended THIS week yet, but attended last week, the streak is still alive!
            streak = 1
            expected_week = current_week - 2
            if expected_week <= 0:
                expected_year -= 1
                expected_week = 52
        else:
            break # Streak broken
            
    return streak

def generate_stats_report() -> str:
    """Generates the analytics summary as a string."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Total Attended
    total_attended = cursor.execute("SELECT COUNT(*) FROM user_actions WHERE action='ATTENDED'").fetchone()[0]
    
    # 2. Platform Breakdown
    platform_stats = cursor.execute('''
        SELECT c.platform, COUNT(u.id) as count
        FROM user_actions u
        JOIN contests c ON u.contest_id = c.id
        WHERE u.action = 'ATTENDED'
        GROUP BY c.platform
        ORDER BY count DESC
    ''').fetchall()
    
    # 3. Streak
    streak = get_streak()
    
    # 4. Missed Contests (Finished but no action logged)
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    missed = cursor.execute('''
        SELECT COUNT(*) FROM contests c
        LEFT JOIN user_actions u ON c.id = u.contest_id
        WHERE c.end_time < ? AND c.status != 'CANCELED' AND u.id IS NULL
    ''', (now_iso,)).fetchone()[0]
    
    conn.close()
    
    lines = []
    lines.append("=========================================")
    lines.append("      ContestPilot Personal Stats        ")
    lines.append("=========================================")
    lines.append(f"🔥 Current Weekly Streak: {streak} weeks")
    lines.append(f"🏆 Total Contests Attended: {total_attended}")
    lines.append(f"⚠️ Unreviewed/Missed Contests: {missed} (Run --review)")
    
    lines.append("\n📊 Platform Breakdown:")
    if platform_stats:
        for p in platform_stats:
            lines.append(f"   - {p['platform'].title()}: {p['count']} contests")
    else:
        lines.append("   - No data yet! Attend a contest first.")
    
    lines.append("=========================================")
    return "\n".join(lines)

def print_stats():
    """Prints a beautiful analytics summary to the console."""
    print("\n" + generate_stats_report() + "\n")
