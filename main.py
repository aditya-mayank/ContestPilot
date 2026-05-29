import logging
import sys
import os

# --- Background mode: redirect stdout/stderr FIRST before any imports ---
# This must happen before anything else so pythonw.exe (no console) doesn't crash
# on SyntaxWarnings or any other output during module loading.
if '--background' in sys.argv:
    _base_dir = os.path.dirname(os.path.abspath(__file__))
    _log_path = os.path.join(_base_dir, 'background.log')
    _log_file = open(_log_path, 'a', encoding='utf-8')
    sys.stdout = _log_file
    sys.stderr = _log_file

# Ensure UTF-8 output on Windows terminals to prevent emoji crashes
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except (AttributeError, Exception):
    pass

from contestpilot.database import is_initialized, init_db, set_preference, get_preference
from contestpilot.utils import get_local_timezone_str
from contestpilot.fetchers import sync_all_fetchers
from contestpilot.calendar_sync import sync_calendar
from contestpilot.email_sync import process_email_notifications
from contestpilot.setup_email import run_email_setup
from contestpilot.attendance_verifier import run_auto_verification
from contestpilot.update_checker import (
    check_for_updates,
    check_for_updates_background,
    notify_if_update_pending,
)

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
        handle = input("   Enter CodeChef username (leave blank to skip auto-verification): ").strip()
        if handle: set_preference('codechef_handle', handle)
        
    if not active_platforms:
        print(" ⚠️  No platforms selected! You can change this later by running with --config.")
        set_preference('platforms', '')
    else:
        set_preference('platforms', ','.join(active_platforms))
        print(f" ✅ Tracking enabled for: {', '.join(p.title() for p in active_platforms)}")
    
    print("\n[3/5] Google Calendar Connection")
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
    import tempfile
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if platform.system() == 'Windows':
        pythonw_path = os.path.join(base_dir, '.venv', 'Scripts', 'pythonw.exe')
        if not os.path.exists(pythonw_path):
            pythonw_path = 'pythonw.exe'
        
        main_path = os.path.join(base_dir, 'main.py')
        
        task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <URI>\\ContestPilotDaily</URI>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger><StartBoundary>2026-01-01T00:00:00</StartBoundary><ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay></CalendarTrigger>
    <CalendarTrigger><StartBoundary>2026-01-01T08:00:00</StartBoundary><ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay></CalendarTrigger>
    <CalendarTrigger><StartBoundary>2026-01-01T16:00:00</StartBoundary><ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay></CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings><StopOnIdleEnd>true</StopOnIdleEnd><RestartOnIdle>false</RestartOnIdle></IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>true</WakeToRun>
    <ExecutionTimeLimit>PT72H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{pythonw_path}</Command>
      <Arguments>"{main_path}" --background</Arguments>
      <WorkingDirectory>{base_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""
        try:
            fd, tmp_path = tempfile.mkstemp(suffix='.xml')
            with os.fdopen(fd, 'w', encoding='utf-16') as f:
                f.write(task_xml)
            
            subprocess.run('schtasks /delete /tn ContestPilotDaily /f', shell=True, capture_output=True)
            result = subprocess.run(f'schtasks /create /tn ContestPilotDaily /xml "{tmp_path}" /f', shell=True, capture_output=True, text=True)
            os.remove(tmp_path)
            
            if result.returncode == 0:
                print(" ✅ Background task installed! It will run invisibly three times a day (12:00 AM, 8:00 AM, and 4:00 PM).")
            else:
                print(" ⚠️  Could not auto-install background task (run terminal as Administrator if you want it).")
        except Exception:
            print(" ⚠️  Could not auto-install background task.")
    else:
        # Mac/Linux: use crontab
        python_path = os.path.join(base_dir, '.venv', 'bin', 'python3')
        main_path = os.path.join(base_dir, 'main.py')
        try:
            cron_job = f"0 0,8,16 * * * cd '{base_dir}' && '{python_path}' '{main_path}' --background"
            cmd = f"(crontab -l 2>/dev/null | grep -v 'ContestPilot'; echo \"{cron_job} # ContestPilot\") | crontab -"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(" ✅ Background task installed! It will run silently three times a day (12:00 AM, 8:00 AM, and 4:00 PM) via cron.")
            else:
                print(" ⚠️  Could not auto-install background task via crontab.")
        except Exception:
            print(" ⚠️  Could not auto-install background task via crontab.")

    print("\n=========================================")
    print(" 🎉 Setup Complete! You are ready to go.")
    print("=========================================\n")

def main():
    if '--background' in sys.argv:
        # stdout/stderr already redirected at module top; just verify
        pass

    if '--check-update' in sys.argv:
        check_for_updates(silent=False)
        return

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
            handle = input("   Enter CodeChef username (leave blank to skip auto-verification): ").strip()
            if handle: set_preference('codechef_handle', handle)
            
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
    
    # --- Update check (runs differently in background vs interactive) ---
    if '--background' in sys.argv:
        try:
            check_for_updates_background()
        except Exception:
            pass  # Never let update check crash the main sync
    else:
        notify_if_update_pending()

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
