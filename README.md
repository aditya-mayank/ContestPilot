# 🏆 ContestPilot

ContestPilot is a smart competitive programming assistant that fetches upcoming contests, syncs them to Google Calendar, tracks history, and sends reminders with minimal setup.

Never miss a Codeforces, CodeChef, LeetCode, or AtCoder contest again. ContestPilot is automated, featuring built-in analytics, attendance tracking, and optional email reports.

## 📌 About the Project

ContestPilot is a Python-based automation agent designed for Competitive Programmers. It fetches upcoming contests from top platforms, pushes them directly to your Google Calendar, and tracks your attendance history.

Unlike traditional scripts, ContestPilot does not require external contest API keys (like Clist.by). It features a minimal setup wizard that creates a local database, connects to your Google Calendar via OAuth, optionally installs a background task (using Windows Task Scheduler or Mac/Linux crontab), and can email you weekly analytical reports.

## ✨ Key Features

* **Smart Calendar Sync**: Events are added to your Google Calendar. If a platform reschedules a contest, ContestPilot automatically detects the change and updates the event instead of duplicating it.
* **Direct Fetchers**: Scrapes directly from LeetCode, Codeforces, CodeChef, and AtCoder endpoints without requiring third-party API keys.
* **Attendance Tracking**: Enter your handles during setup, and ContestPilot will help track your streak (with optional manual review depending on platform support).
* **Automated Email Summaries (Optional)**: Receive a "Weekly CP Report" in your inbox tracking your streak, platform breakdown, and schedule.
* **Background Automation (Optional)**: Can automatically install a silent background task (Windows Task Scheduler or Mac/Linux crontab) to run invisibly twice a day.
* **Secure Local Database**: Uses a local SQLite database to cache history, track streaks, and prevent duplicate notifications.

## 🚀 Getting Started

ContestPilot features a minimal setup wizard designed to reduce user effort. On its first run, it will automatically detect your timezone, create the database, enable supported platforms, and launch the Google sign-in flow.

### Prerequisites

* A Google account.

### Step 1: Install Python (Optional)

You must have Python 3.10 or higher installed. Check your version by opening a terminal and running:
```bash
python --version
# or
python3 --version
```
If you already have Python 3.10+, skip this step! Otherwise:

* **Windows**: Download and install it from [python.org](https://www.python.org/downloads/). **CRITICAL**: Check the box that says **"Add python.exe to PATH"** during installation.
* **Mac**: Install via Homebrew:
  ```bash
  brew install python
  ```
* **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt update
  sudo apt install python3 python3-pip python3-venv
  ```

### Step 2: Download the Project

Clone the repository to your computer:
* **Windows / Mac / Linux**:
  ```bash
  git clone https://github.com/aditya-mayank/ContestPilot.git
  cd ContestPilot
  ```

### Step 3: Get Google Calendar Permissions

Since ContestPilot adds events directly to your personal calendar, you need to grant it permission through Google Cloud:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new Project and search for **Google Calendar API**. Click **Enable**.
3. Go to **Credentials** on the left sidebar.
4. Click **Create Credentials** then **OAuth client ID**. (Select "Desktop App" as the application type).
5. Download the JSON file it gives you.
6. Rename that downloaded file to exactly `credentials.json` and move it directly into your `ContestPilot` folder.

### Step 4: Get a Google App Password (Optional, for Email Alerts)

If you want ContestPilot to send you weekly email summaries, you need a special App Password. **Do not use your actual Gmail password.**
1. Ensure you have 2-Step Verification enabled on your Google Account.
2. Go to your [Google App Passwords](https://myaccount.google.com/apppasswords) page.
3. Type `ContestPilot` as the app name and click **Create**.
4. Copy the 16-character password it generates. You will paste this into the setup wizard later.

### Step 5: Setup & Run

* **Windows**: Double-click the `run.bat` file.
* **Mac / Linux**: Run `./run.sh` in your terminal.

The script will automatically create a virtual environment, install all required packages, and launch the Setup Wizard.

### The Setup Wizard
The ideal flow is simple: Run app → detect timezone → Google sign-in → sync starts automatically.
   * **1/5**: Automatically detects your timezone and sets up the local databases.
   * **2/5**: Asks for your platform handles for attendance tracking (can be skipped).
   * **3/5**: Opens a browser asking you to log into your Google Account. Click **Allow** (saves token automatically).
   * **4/5**: Asks if you want to configure weekly Email Alerts.
   * **5/5**: Optionally installs the background task to run automatically via Windows Task Scheduler or Mac/Linux `crontab`.

It will then fetch your contests, sync your calendar, and print your personal CP Stats!

## ⚡ Quick Actions

For the best user experience, your project contains a `Quick_Actions` folder. Inside, you will find easy launcher scripts so you don't have to type commands again:

(Mac/Linux users can use the equivalent `.sh` files in the same folder!)

* 🗑️ `clear_calendar`: Instantly wipes all ContestPilot events from your calendar.
* 📊 `view_stats`: Displays your CP Report Card and current streak.
* ⚙️ `configure_settings`: Opens the wizard to update your Handles and Email preferences.
* 🛑 `uninstall_and_stop`: Stops all background tasks and disables email alerts.
* 🔄 `update_app`: Automatically pulls the latest updates from GitHub.
* 📝 `review_contests`: Asks you if you attended past CodeChef contests so you can maintain your streak.

## 🔒 Security & Privacy Notes

* **100% Local Processing**: ContestPilot runs securely on your computer. Your `contestpilot.db` (which stores your preferences and email settings), `credentials.json`, and `token.json` are automatically excluded from version control so they are never accidentally pushed to GitHub.
* ContestPilot never asks for your actual Google password. It uses standard OAuth2 tokens.
* For Email Summaries, it strictly requires a 16-character [Google App Password](https://myaccount.google.com/apppasswords), meaning your actual Gmail password is never touched.

Happy Coding! Let ContestPilot handle the schedule while you handle the algorithms.
