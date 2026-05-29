"""
Update Checker for ContestPilot.

Compares the local VERSION file against the remote VERSION on GitHub.
When a newer version is detected, notifies the user via console output
and (if email is enabled) queues an email notification.

This uses the GitHub raw content URL — no API key required, no rate-limit
issues for the frequency we check (3x/day via background task).
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

# --- Configuration ---
GITHUB_RAW_URL = (
    "https://raw.githubusercontent.com/aditya-mayank/ContestPilot/main/VERSION"
)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_VERSION_PATH = os.path.join(BASE_DIR, "VERSION")


def _read_local_version() -> str:
    """Read the local VERSION file."""
    try:
        with open(LOCAL_VERSION_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.warning("VERSION file not found locally — assuming 0.0.0")
        return "0.0.0"


def _fetch_remote_version() -> str | None:
    """Fetch the VERSION file from GitHub (raw content)."""
    try:
        resp = requests.get(GITHUB_RAW_URL, timeout=10)
        resp.raise_for_status()
        return resp.text.strip()
    except Exception as e:
        logger.debug(f"Could not fetch remote version: {e}")
        return None


def _parse_version(version_str: str) -> tuple:
    """Parse a semver-like string into a comparable tuple of ints."""
    try:
        parts = version_str.split(".")
        return tuple(int(p) for p in parts)
    except (ValueError, AttributeError):
        return (0, 0, 0)


def check_for_updates(silent: bool = False) -> bool:
    """
    Check if a newer version of ContestPilot is available on GitHub.

    Args:
        silent: If True, only log at debug level (for background runs).
                If False, always print the result to the console.

    Returns:
        True if an update is available, False otherwise.
    """
    local_version = _read_local_version()
    remote_version = _fetch_remote_version()

    if remote_version is None:
        if not silent:
            print("  ⚠️  Could not check for updates (no internet?).")
        return False

    local_tuple = _parse_version(local_version)
    remote_tuple = _parse_version(remote_version)

    if remote_tuple > local_tuple:
        msg = (
            f"\n"
            f"  ╔══════════════════════════════════════════════════════╗\n"
            f"  ║         🚀 ContestPilot Update Available!           ║\n"
            f"  ║                                                      ║\n"
            f"  ║   Installed:  v{local_version:<38s}║\n"
            f"  ║   Available:  v{remote_version:<38s}║\n"
            f"  ║                                                      ║\n"
            f"  ║   Run the 'update_app' Quick Action to update,      ║\n"
            f"  ║   or run:  git pull                                  ║\n"
            f"  ╚══════════════════════════════════════════════════════╝\n"
        )
        if silent:
            logger.info(msg)
        else:
            print(msg)
        return True
    else:
        if not silent:
            print(f"  ✅ ContestPilot is up to date (v{local_version}).")
        return False


def _send_update_email(local_version: str, remote_version: str):
    """Send an email notification about the available update."""
    from .email_sync import is_email_configured, send_email

    if not is_email_configured():
        return

    subject = f"[ContestPilot] 🚀 Update Available — v{remote_version}"
    body = (
        f"Hey there!\n\n"
        f"A new version of ContestPilot is available on GitHub.\n\n"
        f"  Installed version:  v{local_version}\n"
        f"  Available version:  v{remote_version}\n\n"
        f"To update, simply run the 'update_app' Quick Action:\n"
        f"  • Windows: Double-click  Quick_Actions/Windows/update_app.bat\n"
        f"  • Mac/Linux: Run  Quick_Actions/Mac_Linux/update_app.sh\n\n"
        f"Or open a terminal in the ContestPilot folder and run:\n"
        f"  git pull\n\n"
        f"--\n"
        f"Happy Coding!\n"
        f"ContestPilot\n"
    )

    send_email(subject, body)


def check_for_updates_background():
    """
    Background-mode update check.

    Called during the automated background run (3x/day).
    If an update is available:
      1. Stores the pending version in the DB (for interactive banner)
      2. Sends an email notification (only once per new version)
    """
    from .database import get_preference, set_preference

    local_version = _read_local_version()
    remote_version = _fetch_remote_version()

    if remote_version is None:
        return  # No internet, skip silently

    local_tuple = _parse_version(local_version)
    remote_tuple = _parse_version(remote_version)

    if remote_tuple > local_tuple:
        # Store pending update info in the database (for interactive banner)
        set_preference("pending_update_version", remote_version)

        # Send email — but only once per version to avoid spamming
        already_emailed_for = get_preference("update_email_sent_for")
        if already_emailed_for != remote_version:
            logger.info(
                f"[Update Checker] New version v{remote_version} detected "
                f"(current: v{local_version}). Sending email notification..."
            )
            _send_update_email(local_version, remote_version)
            set_preference("update_email_sent_for", remote_version)
        else:
            logger.debug(
                f"[Update Checker] Update v{remote_version} already emailed, skipping."
            )
    else:
        # Clear any stale pending update (e.g., user already updated)
        set_preference("pending_update_version", "")
        set_preference("update_email_sent_for", "")


def notify_if_update_pending():
    """
    Called at the start of any interactive (non-background) run.
    If the background checker found an update, notify the user.
    """
    from .database import get_preference

    pending = get_preference("pending_update_version")
    if pending and pending.strip():
        local_version = _read_local_version()
        local_tuple = _parse_version(local_version)
        pending_tuple = _parse_version(pending)

        if pending_tuple > local_tuple:
            print(
                f"\n"
                f"  ╔══════════════════════════════════════════════════════╗\n"
                f"  ║         🚀 ContestPilot Update Available!           ║\n"
                f"  ║                                                      ║\n"
                f"  ║   Installed:  v{local_version:<38s}║\n"
                f"  ║   Available:  v{pending:<38s}║\n"
                f"  ║                                                      ║\n"
                f"  ║   Run the 'update_app' Quick Action to update,      ║\n"
                f"  ║   or run:  git pull                                  ║\n"
                f"  ╚══════════════════════════════════════════════════════╝\n"
            )
