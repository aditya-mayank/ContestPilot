import logging
import sys
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
    print("\n[1/4] Initializing Engine...")
    
    # 1. Initialize the database
    init_db()
    print(" ✅ Database created successfully.")

    # 2. Store default preferences
    local_tz = get_local_timezone_str()
    set_preference('timezone', local_tz)
    print(f" ✅ Auto-detected timezone: {local_tz}")
    
    print("\n[1.5/4] Platform Selection & Usernames")
    print(" Which contest platforms do you want to track? (y/n)")
    platforms = []
    
    lc_ans = input(" - LeetCode? (y/N): ").strip().lower()
    if lc_ans == 'y': 
        platforms.append('leetcode')
        handle = input("   Enter LeetCode username (for auto-verification) or press Enter to skip: ").strip()
        if handle: set_preference('leetcode_handle', handle)
        
    cf_ans = input(" - Codeforces? (y/N): ").strip().lower()
    if cf_ans == 'y': 
        platforms.append('codeforces')
        handle = input("   Enter Codeforces handle (for auto-verification) or press Enter to skip: ").strip()
        if handle: set_preference('codeforces_handle', handle)
        
    if input(" - CodeChef? (y/N): ").strip().lower() == 'y': platforms.append('codechef')
    if input(" - HackerRank? (y/N): ").strip().lower() == 'y': platforms.append('hackerrank')
    
    ac_ans = input(" - AtCoder? (y/N): ").strip().lower()
    if ac_ans == 'y': 
        platforms.append('atcoder')
        handle = input("   Enter AtCoder username (for auto-verification) or press Enter to skip: ").strip()
        if handle: set_preference('atcoder_handle', handle)
    
    if not platforms:
        print(" [Warning] No platforms selected. Defaulting to LeetCode and Codeforces.")
        platforms = ['leetcode', 'codeforces']
    
    set_preference('platforms', ','.join(platforms))
    
    print("\n[2/4] Google Calendar Connection")
    print(" ContestPilot needs permission to add events to your Calendar.")
    print(" A browser window will now open. Please sign in with Google.")
    input(" Press Enter to open the browser...")
    
    from contestpilot.calendar_sync import get_credentials
    get_credentials()
    print(" ✅ Calendar connected successfully.")
    
    print("\n[3/4] Email Notifications (Optional)")
    print(" ContestPilot can send you beautiful Daily/Weekly summaries")
    print(" and alert you if a contest is canceled or moved.")
    ans = input(" Do you want to configure Email alerts now? (y/N): ").strip().lower()
    if ans == 'y':
        run_email_setup()
    else:
        print(" ⏭️  Skipped. You can always set this up later using '.\\run.bat --setup-email'")
        
    print("\n[4/4] Local Background Automation")
    print(" For ContestPilot to be fully autonomous, it needs to run automatically in the background.")
    print(" If you plan to use GitHub Actions instead, you can skip this.")
    ans = input(" Install a scheduled task to run silently every day at 8:00 AM? (y/N): ").strip().lower()
    if ans == 'y':
        import os
        import subprocess
        base_dir = os.path.dirname(os.path.abspath(__file__))
        vbs_path = os.path.join(base_dir, 'run_invisible.vbs')
        bat_path = os.path.join(base_dir, 'run.bat')
        
        # We pass --background so it doesn't pause
        cmd = f'schtasks /create /tn "ContestPilotDaily" /tr "wscript.exe \\"{vbs_path}\\" \\"{bat_path}\\" --background" /sc daily /st 08:00 /f'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(" ✅ Background task installed! It will run invisibly every morning.")
            else:
                print(f" ⚠️ Failed to install background task. Try running as Administrator.")
                print(f" Error: {result.stderr.strip()}")
        except Exception as e:
            print(f" ⚠️ Failed to install background task: {e}")
    else:
        print(" ⏭️  Skipped.")

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
    print(f"\n[ContestPilot] Starting sync... (Timezone: {tz})")
    
    # Step 1: Fetch and rank contests
    sync_all_fetchers()
    
    # Step 2: Push to Google Calendar
    print("\n[ContestPilot] Starting Google Calendar sync...")
    sync_calendar()
    
    # Step 3: Auto-Verify Attendance for past contests
    print("\n[ContestPilot] Auto-verifying recent contest attendance...")
    run_auto_verification()
    
    # Step 4: Send Email Notifications (this marks notifications as sent)
    process_email_notifications()

if __name__ == '__main__':
    main()
