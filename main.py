import logging
import sys

# Ensure UTF-8 output on Windows terminals to prevent emoji crashes
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

from contestpilot.database import is_initialized, init_db, set_preference, get_preference
from contestpilot.utils import get_local_timezone_str
from contestpilot.fetchers import sync_all_fetchers
from contestpilot.calendar_sync import sync_calendar
from contestpilot.email_sync import process_email_notifications
from contestpilot.setup_email import run_email_setup
from contestpilot.attendance_verifier import run_auto_verification

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def run_setup_wizard():
    print("\n=========================================")
    print("      🚀 Welcome to ContestPilot!        ")
    print("=========================================")
    print("ContestPilot is your personal Competitive Programming assistant.")
    print("It will automatically track upcoming contests, filter them by")
    print("your priorities, sync them to your Google Calendar, and send")
    print("you summaries so you never miss a match!")
    print("-----------------------------------------")
    
    print("\n[1/5] Initializing Engine...")
    init_db()
    
    local_tz = get_local_timezone_str()
    set_preference('timezone', local_tz)
    print(f" ✅ Auto-detected timezone: {local_tz}")
    
    # Enable all supported platforms by default
    platforms = ['leetcode', 'codeforces', 'codechef', 'atcoder']
    set_preference('platforms', ','.join(platforms))
    print(" ✅ Tracking enabled for: LeetCode, Codeforces, CodeChef, AtCoder")
    
    print("\n[2/5] Auto-Verification Handles (Optional)")
    print(" Leave blank to skip.")
    handle = input(" - LeetCode username: ").strip()
    if handle: set_preference('leetcode_handle', handle)
    
    handle = input(" - Codeforces handle: ").strip()
    if handle: set_preference('codeforces_handle', handle)
    
    handle = input(" - AtCoder username: ").strip()
    if handle: set_preference('atcoder_handle', handle)
    
    print("\n[3/5] Google Calendar Connection")
    import os
    import time
    if not os.path.exists('token.json'):
        print(" ContestPilot needs permission to add events to your Calendar.")
        print(" Opening browser to connect Google Calendar...")
        time.sleep(1) # Give user a second to read before browser opens
        from contestpilot.calendar_sync import get_credentials
        get_credentials()
        print(" ✅ Calendar connected successfully.")
    else:
        print(" ✅ Calendar already connected.")
        
    print("\n[4/5] Email Notifications (Optional)")
    ans = input(" - Do you want to configure Weekly Email alerts? (y/N): ").strip().lower()
    if ans == 'y':
        run_email_setup()

    print("\n[5/5] Local Background Automation")
    import subprocess
    base_dir = os.path.dirname(os.path.abspath(__file__))
    vbs_path = os.path.join(base_dir, 'run_invisible.vbs')
    bat_path = os.path.join(base_dir, 'run.bat')
    
    cmd = f'powershell -Command "Register-ScheduledTask -TaskName \'ContestPilotDaily\' -Trigger (New-ScheduledTaskTrigger -Daily -At 8am) -Action (New-ScheduledTaskAction -Execute \'wscript.exe\' -Argument \'\\"{vbs_path}\\" \\"{bat_path} --background\\"\') -Force"'
    try:
        # Run silently, do not capture or crash
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(" ✅ Background task installed! It will run invisibly every morning at 8:00 AM.")
        else:
            print(" ⚠️  Could not auto-install background task (run terminal as Administrator if you want it).")
    except Exception:
        print(" ⚠️  Could not auto-install background task.")

    print("\n=========================================")
    print(" 🎉 Setup Complete! You are ready to go.")
    print("=========================================\n")
def main():
    if '--setup-email' in sys.argv:
        run_email_setup()
        return

    if '--stop-email' in sys.argv:
        set_preference('email_enabled', 'false')
        print("[ContestPilot] Email notifications have been DISABLED.")
        return
        
    if '--stop-all' in sys.argv:
        import os
        set_preference('email_enabled', 'false')
        print("[ContestPilot] All notifications disabled.")
        print("[ContestPilot] Removing background task...")
        os.system('schtasks /delete /tn "ContestPilotDaily" /f')
        print("[ContestPilot] Uninstalled successfully. The script will no longer run automatically.")
        return
    if '--config' in sys.argv:
        print("\n=========================================")
        print("      🛠️ ContestPilot Configuration     ")
        print("=========================================")
        print("\n[1] Auto-Verification Handles")
        handle = input(" - Enter LeetCode username: ").strip()
        if handle: set_preference('leetcode_handle', handle)
        
        handle = input(" - Enter Codeforces handle: ").strip()
        if handle: set_preference('codeforces_handle', handle)
        
        handle = input(" - Enter AtCoder username: ").strip()
        if handle: set_preference('atcoder_handle', handle)
        
        print("\n[2] Email Summaries")
        ans = input(" - Do you want to configure Email alerts? (y/N): ").strip().lower()
        if ans == 'y':
            run_email_setup()
            
        print("\n ✅ Configuration saved!\n")
        return

    # --- Analytics & History Commands ---
    from contestpilot.analytics import interactive_review, mark_attendance, print_stats
    
    if '--review' in sys.argv:
        interactive_review()
        return
        
    if '--stats' in sys.argv:
        print_stats()
        return
        
    for i, arg in enumerate(sys.argv):
        if arg == '--attend' and i + 1 < len(sys.argv):
            mark_attendance(sys.argv[i+1], 'ATTENDED')
            return
        elif arg == '--skip' and i + 1 < len(sys.argv):
            mark_attendance(sys.argv[i+1], 'SKIPPED')
            return

    if not is_initialized():
        run_setup_wizard()
    
    tz = get_preference('timezone')
    print(f"\n⚡ [ContestPilot] Waking up... (Timezone: {tz})")
    
    print("\n[1/4] Fetching latest contests...")
    sync_all_fetchers()
    
    print("\n[2/4] Syncing to Google Calendar...")
    sync_calendar()
    
    print("\n[3/4] Auto-verifying recent attendance...")
    run_auto_verification()
    print("\n[4/4] Sending automated reports/emails...")
    process_email_notifications()
    
    print("\n 🎯 All caught up! ContestPilot goes back to sleep.")
    
    if '--background' not in sys.argv:
        from contestpilot.analytics import print_stats
        print_stats()

if __name__ == '__main__':
    main()
