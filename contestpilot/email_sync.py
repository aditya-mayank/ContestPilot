import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from .database import get_preference, get_pending_notifications, mark_notification_sent, get_connection

logger = logging.getLogger(__name__)

def is_email_configured() -> bool:
    return get_preference('email_enabled') == 'true'

def send_email(subject: str, body: str):
    """Sends an email using configured SMTP credentials."""
    smtp_server = get_preference('smtp_server')
    smtp_port = int(get_preference('smtp_port') or 587)
    smtp_user = get_preference('smtp_user')
    smtp_pass = get_preference('smtp_pass')
    recipient = get_preference('email_recipient')

    if not all([smtp_server, smtp_port, smtp_user, smtp_pass, recipient]):
        logger.error("Email is enabled but SMTP credentials or recipient are missing.")
        return False

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        logger.info(f"Successfully sent email to {recipient}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

def send_periodic_summaries():
    if not is_email_configured():
        return

    from .utils import utc_now_iso
    import datetime
    from .database import set_preference

    now = datetime.datetime.now(datetime.timezone.utc)
    
    # Daily Summary
    last_daily = get_preference('last_daily_summary')
    if not last_daily or (now - datetime.datetime.fromisoformat(last_daily)).total_seconds() > 86400:
        # Fetch upcoming contests in next 24h
        conn = get_connection()
        cursor = conn.cursor()
        next_24h = (now + datetime.timedelta(days=1)).isoformat()
        rows = cursor.execute('SELECT name, platform, start_time FROM contests WHERE start_time > ? AND start_time < ?', (now.isoformat(), next_24h)).fetchall()
        conn.close()
        
        if rows:
            subject = "[ContestPilot] Daily Summary: Upcoming Contests"
            body = f"You have {len(rows)} contests in the next 24 hours:\n\n"
            for r in rows:
                body += f"- {r['name']} ({r['platform'].title()}) at {r['start_time']}\n"
            if send_email(subject, body):
                set_preference('last_daily_summary', now.isoformat())

    # Weekly Summary
    last_weekly = get_preference('last_weekly_summary')
    if not last_weekly or (now - datetime.datetime.fromisoformat(last_weekly)).total_seconds() > 7 * 86400:
        # Fetch upcoming contests in next 7 days
        conn = get_connection()
        cursor = conn.cursor()
        next_7d = (now + datetime.timedelta(days=7)).isoformat()
        rows = cursor.execute('SELECT name, platform, start_time FROM contests WHERE start_time > ? AND start_time < ?', (now.isoformat(), next_7d)).fetchall()
        conn.close()
        
        if rows:
            from .analytics import get_streak
            streak = get_streak()
            subject = "[ContestPilot] Weekly Summary: Upcoming Contests & Stats"
            body = f"You have {len(rows)} contests coming up this week:\n\n"
            for r in rows:
                body += f"- {r['name']} ({r['platform'].title()}) at {r['start_time']}\n"
            
            body += f"\n🔥 Current Weekly Streak: {streak} weeks\n"
            body += "\n--\nHappy Coding!\nContestPilot\n\nTo stop receiving these emails, run '.\\run.bat --stop-email' on your machine."
            
            if send_email(subject, body):
                set_preference('last_weekly_summary', now.isoformat())

def process_email_notifications():
    """Reads pending notifications from the DB and sends a batch email."""
    if not is_email_configured():
        return
        
    notifications = get_pending_notifications()
    if notifications:
        logger.info(f"Found {len(notifications)} pending notifications. Preparing email batch...")

        subject = f"[ContestPilot] {len(notifications)} Contest Updates"
        body = "Here are your latest competitive programming updates:\n\n"
        
        for notif in notifications:
            body += f"[{notif['type']}] {notif['message']}\n"
            
        body += "\n--\nHappy Coding!\nContestPilot\n\nTo stop receiving these emails, run '.\\run.bat --stop-email' on your machine."

        success = send_email(subject, body)
        
        if success:
            for notif in notifications:
                mark_notification_sent(notif['id'])
                
    # Also trigger summaries
    send_periodic_summaries()
