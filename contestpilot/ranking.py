import datetime
import logging
from typing import Tuple

from .models import Contest
from .database import get_preference
from .utils import get_local_timezone_str

logger = logging.getLogger(__name__)

def parse_time_range(time_range_str: str) -> Tuple[datetime.time, datetime.time]:
    """Parses a time range string like '22:00-08:00' into two time objects."""
    start_str, end_str = time_range_str.split('-')
    start_time = datetime.datetime.strptime(start_str.strip(), '%H:%M').time()
    end_time = datetime.datetime.strptime(end_str.strip(), '%H:%M').time()
    return start_time, end_time

def is_time_in_range(t: datetime.time, start: datetime.time, end: datetime.time) -> bool:
    """Checks if time t falls within start and end, handling midnight wrap-around."""
    if start <= end:
        return start <= t <= end
    else: # crosses midnight
        return start <= t or t <= end

def get_contest_local_time(contest: Contest, tz_str: str) -> datetime.datetime:
    """Returns the contest start time in the user's local timezone."""
    try:
        from dateutil import tz
        utc_dt = datetime.datetime.fromisoformat(contest.start_time.replace('Z', '+00:00'))
        local_zone = tz.gettz(tz_str)
        if not local_zone:
            # fallback to UTC if tz string is somehow invalid
            local_zone = datetime.timezone.utc
        return utc_dt.astimezone(local_zone)
    except Exception as e:
        logger.warning(f"Error converting timezone for {contest.id}: {e}")
        return datetime.datetime.fromisoformat(contest.start_time.replace('Z', '+00:00'))

def rank_contest(contest: Contest) -> Tuple[str, str]:
    """
    Evaluates a contest based on duration, platform, quiet hours, and busy hours.
    Returns: (priority, reason)
    Priorities: 'high', 'medium', 'low', 'skip'
    """
    tz_str = get_preference('timezone') or 'UTC'
    local_start = get_contest_local_time(contest, tz_str)
    
    # 1. Filter by duration
    duration_hours = contest.duration_seconds / 3600.0
    if duration_hours < 1:
        return "low", f"Low Priority: Too short ({duration_hours:.1f} hours)."
    if duration_hours > 24:
        return "low", f"Low Priority: Long running challenge ({duration_hours:.1f} hours)."

    # 2. Check Quiet Hours (Default: 22:00-08:00)
    quiet_hours_str = get_preference('quiet_hours') or '22:00-08:00'
    start_q, end_q = parse_time_range(quiet_hours_str)
    if is_time_in_range(local_start.time(), start_q, end_q):
        return "low", f"Low Priority: Starts during quiet hours ({quiet_hours_str})."

    # 3. Check Busy Hours (Default: 09:00-17:00 Mon-Fri)
    # We only check busy hours if it's a weekday (0 = Monday, 4 = Friday)
    if local_start.weekday() < 5:
        busy_hours_str = get_preference('busy_hours') or '09:00-17:00'
        start_b, end_b = parse_time_range(busy_hours_str)
        if is_time_in_range(local_start.time(), start_b, end_b):
            return "low", f"Low Priority: Starts during weekday busy hours ({busy_hours_str})."

    # 4. Default to Medium or High based on platform
    # We consider major platforms High priority by default, Clist others as Medium.
    major_platforms = ['codeforces', 'leetcode', 'atcoder', 'hackerrank']
    if contest.platform.lower() in major_platforms:
        return "high", "High Priority: Favorable time on a major platform."
    
    return "medium", "Medium Priority: Favorable time."
