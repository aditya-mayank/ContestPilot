import logging
import requests
import datetime
from .database import get_connection, get_preference, set_preference
from .analytics import mark_attendance
from .models import Contest

logger = logging.getLogger(__name__)

def verify_leetcode(handle: str, contests: list):
    url = 'https://leetcode.com/graphql'
    query = '''
    query userContestRankingInfo($username: String!) {
      userContestRankingHistory(username: $username) {
        attended
        contest { title }
      }
    }
    '''
    try:
        r = requests.post(url, json={'query': query, 'variables': {'username': handle}}, timeout=10)
        if r.status_code == 200:
            history = r.json().get('data', {}).get('userContestRankingHistory', [])
            attended_titles = [h['contest']['title'] for h in history if h.get('attended') and h.get('contest')]
            
            for c in contests:
                if c.name in attended_titles:
                    logger.info(f"Auto-Verified LeetCode: {c.name}")
                    mark_attendance(c.id, 'ATTENDED')
                else:
                    end_dt = datetime.datetime.fromisoformat(c.end_time.replace('Z', '+00:00'))
                    if (datetime.datetime.now(datetime.timezone.utc) - end_dt).total_seconds() > 604800:
                        logger.info(f"Auto-Skipped LeetCode: {c.name} (ended >7 days ago)")
                        mark_attendance(c.id, 'SKIPPED')
    except Exception as e:
        logger.error(f"Failed to verify LeetCode for {handle}: {e}")

def verify_codeforces(handle: str, contests: list):
    url = f'https://codeforces.com/api/user.rating?handle={handle}'
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            history = r.json().get('result', [])
            attended_ids = [str(h['contestId']) for h in history]
            
            for c in contests:
                if c.source_id in attended_ids:
                    logger.info(f"Auto-Verified Codeforces: {c.name}")
                    mark_attendance(c.id, 'ATTENDED')
                else:
                    end_dt = datetime.datetime.fromisoformat(c.end_time.replace('Z', '+00:00'))
                    if (datetime.datetime.now(datetime.timezone.utc) - end_dt).total_seconds() > 604800:
                        logger.info(f"Auto-Skipped Codeforces: {c.name} (ended >7 days ago)")
                        mark_attendance(c.id, 'SKIPPED')
    except Exception as e:
        logger.error(f"Failed to verify Codeforces for {handle}: {e}")

def verify_atcoder(handle: str, contests: list):
    # For AtCoder, we check if they made any submissions during the contest window
    url = f'https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={handle}&from_second=0'
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            submissions = r.json()
            sub_times = [s['epoch_second'] for s in submissions]
            
            for c in contests:
                start_dt = datetime.datetime.fromisoformat(c.start_time.replace('Z', '+00:00'))
                end_dt = datetime.datetime.fromisoformat(c.end_time.replace('Z', '+00:00'))
                
                start_sec = start_dt.timestamp()
                end_sec = end_dt.timestamp()
                
                # Check if any submission falls within [start, end]
                attended = any(start_sec <= t <= end_sec for t in sub_times)
                
                if attended:
                    logger.info(f"Auto-Verified AtCoder: {c.name}")
                    mark_attendance(c.id, 'ATTENDED')
                else:
                    if (datetime.datetime.now(datetime.timezone.utc) - end_dt).total_seconds() > 86400:
                        logger.info(f"Auto-Skipped AtCoder: {c.name} (ended >24h ago)")
                        mark_attendance(c.id, 'SKIPPED')
    except Exception as e:
        logger.error(f"Failed to verify AtCoder for {handle}: {e}")

def run_auto_verification():
    """Runs through past unverified contests and checks platform APIs for attendance."""
    conn = get_connection()
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # Get all contests that have ended but haven't been marked attended/skipped
    rows = conn.execute('''
        SELECT c.* FROM contests c
        LEFT JOIN user_actions ua ON c.id = ua.contest_id AND ua.action IN ('ATTENDED', 'SKIPPED')
        WHERE ua.id IS NULL AND c.end_time < ?
    ''', (now_iso,)).fetchall()
    conn.close()

    if not rows:
        return

    # Group by platform
    unverified = {'leetcode': [], 'codeforces': [], 'atcoder': []}
    for r in rows:
        plat = r['platform'].lower()
        if plat in unverified:
            c = Contest(**dict(r))
            unverified[plat].append(c)

    # LeetCode
    if unverified['leetcode']:
        handle = get_preference('leetcode_handle')
        if handle:
            verify_leetcode(handle, unverified['leetcode'])

    # Codeforces
    if unverified['codeforces']:
        handle = get_preference('codeforces_handle')
        if handle:
            verify_codeforces(handle, unverified['codeforces'])
            
    # AtCoder
    if unverified['atcoder']:
        handle = get_preference('atcoder_handle')
        if handle:
            verify_atcoder(handle, unverified['atcoder'])
