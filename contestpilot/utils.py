import datetime
from tzlocal import get_localzone
import logging

logger = logging.getLogger(__name__)

def get_local_timezone_str() -> str:
    """Returns the local timezone as a string (e.g., 'Asia/Kolkata')."""
    try:
        local_tz = get_localzone()
        return str(local_tz)
    except Exception as e:
        logger.warning(f"Could not detect local timezone, defaulting to UTC: {e}")
        return "UTC"

def utc_now_iso() -> str:
    """Returns current UTC time in ISO8601 format."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
