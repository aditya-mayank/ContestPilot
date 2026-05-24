"""
ARCHITECTURE NOTES:
1. Setup Wizard Flow: Developers hate configuring boilerplate. The wizard is designed 
   to capture everything necessary (timezones, handles, OAuth tokens) in a single, 
   guided, 30-second flow so they never have to touch a configuration file manually.
2. Why Background Tasks? A simple script requires the user to remember to run it. 
   ContestPilot acts as a true stateful agent: by injecting an OS-level scheduled 
   task (Windows Task Scheduler or crontab), it runs invisibly twice a day. This 
   guarantees the user never misses a contest reschedule without draining their battery.
"""

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
    
    print("\n[2/5] Platform Selection & Handles")
    print(" Select the platforms you want to track. Only selected platforms will appear in your calendar and emails.")
    
    active_platforms = []
    
    ans = input(" - Do you participate in LeetCode? (Y/N): ").strip().lower()
    if ans == 'y':
        active_platforms.append('leetcode')
        handle = input("   Enter LeetCode username (leave blank to skip auto-verification): ").strip()
        if handle: set_preference('leetcode_handle', handle)

    ans = input(" - Do you participate in Codeforces? (Y/N): ").strip().lower()
    if ans == 'y':
        active_platforms.append('codeforces')
        handle = input("   Enter Codeforces handle (leave blank to skip auto-verification): ").strip()
        if handle: set_preference('codeforces_handle', handle)

    ans = input(" - Do you participate in AtCoder? (Y/N): ").strip().lower()
    if ans == 'y':
        active_platforms.append('atcoder')
        handle = input("   Enter AtCoder username (leave blank to skip auto-verification): ").strip()
        if handle: set_preference('atcoder_handle', handle)

    ans = input(" - Do you participate in CodeChef? (Y/N): ").strip().lower()
    if ans == 'y':
        active_platforms.append('codechef')
        print("   (Note: CodeChef does not support auto-verification, so attendances must be marked manually)")
        
    if not active_platforms:
        print(" ⚠️  No platforms selected! You can change this later by running with --config.")
        set_preference('platforms', '')
    else:
        set_preference('platforms', ','.join(active_platforms))
        print(f" ✅ Tracking enabled for: {', '.join(p.title() for p in active_platforms)}")
    
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
    ans = input(" - Do you want to configure Weekly Email alerts? (Y/N): ").strip().lower()
    if ans == 'y':
        run_email_setup()

    print("\n[5/5] Local Background Automation")
    import subprocess
    import platform
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if platform.system() == 'Windows':
        vbs_path = os.path.join(base_dir, 'run_invisible.vbs')
        bat_path = os.path.join(base_dir, 'run.bat')
        cmd = f'powershell -Command "$t1 = New-ScheduledTaskTrigger -Daily -At 2am; $t2 = New-ScheduledTaskTrigger -Daily -At 2pm; Register-ScheduledTask -TaskName \'ContestPilotDaily\' -Trigger $t1, $t2 -Action (New-ScheduledTaskAction -Execute \'wscript.exe\' -Argument \'\\"{vbs_path}\\" \\"{bat_path}\\" --background\') -Force"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(" ✅ Background task installed! It will run invisibly twice a day (2:00 AM and 2:00 PM).")
            else:
                print(" ⚠️  Could not auto-install background task (run terminal as Administrator if you want it).")
        except Exception:
            print(" ⚠️  Could not auto-install background task.")
    else:
        # Mac/Linux: use crontab
        run_sh_path = os.path.join(base_dir, 'run.sh')
        try:
            os.chmod(run_sh_path, 0o755) # Make executable
            cron_job = f"0 2,14 * * * cd '{base_dir}' && ./run.sh --background"
            cmd = f"(crontab -l 2>/dev/null | grep -v 'ContestPilot'; echo \"{cron_job} # ContestPilot\") | crontab -"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(" ✅ Background task installed! It will run silently twice a day (2:00 AM and 2:00 PM) via cron.")
            else:
                print(" ⚠️  Could not auto-install background task via crontab.")
        except Exception:
            print(" ⚠️  Could not auto-install background task via crontab.")

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
        import platform
        set_preference('email_enabled', 'false')
        print("[ContestPilot] All notifications disabled.")
        print("[ContestPilot] Removing background task...")
        
        if platform.system() == 'Windows':
            os.system('schtasks /delete /tn "ContestPilotDaily" /f')
        else:
            os.system("crontab -l 2>/dev/null | grep -v 'ContestPilot' | crontab -")
            
        print("[ContestPilot] Uninstalled successfully. The script will no longer run automatically.")
        return

    if '--email-stats' in sys.argv:
        from contestpilot.email_sync import force_send_stats_email
        force_send_stats_email()
        return

    if '--clear-calendar' in sys.argv:
        from contestpilot.calendar_sync import clear_all_contests
        clear_all_contests()
        return
    if '--config' in sys.argv:
        print("\n=========================================")
        print("      🛠️ ContestPilot Configuration     ")
        print("=========================================")
        print("\n[1] Platform Selection & Handles")
        active_platforms = []
        
        ans = input(" - Do you participate in LeetCode? (Y/N): ").strip().lower()
        if ans == 'y':
            active_platforms.append('leetcode')
            handle = input("   Enter LeetCode username (leave blank to skip auto-verification): ").strip()
            if handle: set_preference('leetcode_handle', handle)

        ans = input(" - Do you participate in Codeforces? (Y/N): ").strip().lower()
        if ans == 'y':
            active_platforms.append('codeforces')
            handle = input("   Enter Codeforces handle (leave blank to skip auto-verification): ").strip()
            if handle: set_preference('codeforces_handle', handle)

        ans = input(" - Do you participate in AtCoder? (Y/N): ").strip().lower()
        if ans == 'y':
            active_platforms.append('atcoder')
            handle = input("   Enter AtCoder username (leave blank to skip auto-verification): ").strip()
            if handle: set_preference('atcoder_handle', handle)

        ans = input(" - Do you participate in CodeChef? (Y/N): ").strip().lower()
        if ans == 'y':
            active_platforms.append('codechef')
            print("   (Note: CodeChef does not support auto-verification, so attendances must be marked manually)")
            
        if not active_platforms:
            print(" ⚠️  No platforms selected!")
            set_preference('platforms', '')
        else:
            set_preference('platforms', ','.join(active_platforms))
            print(f" ✅ Tracking enabled for: {', '.join(p.title() for p in active_platforms)}")
            
        print("\n[2] Email Summaries")
        ans = input(" - Do you want to configure Email alerts? (Y/N): ").strip().lower()
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
