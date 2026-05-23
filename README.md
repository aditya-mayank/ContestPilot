# 🏆 ContestPilot

Your Autonomous Competitive Programming Scheduler & Coach.

Never miss a Codeforces, CodeChef, LeetCode, or AtCoder contest again. ContestPilot is fully automated, with built-in analytics, auto-verification, and email reports!

## 📌 About the Project

ContestPilot is a powerful Python automation agent designed for Competitive Programmers. It natively fetches upcoming contests from top platforms, pushes them directly to your Google Calendar, and tracks your attendance.

Unlike traditional scripts, ContestPilot does not require external contest API keys (like Clist.by). It features a completely zero-prompt setup wizard that creates a local database, connects to your Google Calendar via OAuth, installs a silent Windows background task, and emails you weekly analytical reports.

## ✨ Key Features

* **Native Fetchers**: Scrapes directly from official LeetCode, Codeforces, CodeChef, and AtCoder endpoints. Zero contest-platform API keys needed.
* **Smart Calendar Sync**: Events are added to your Google Calendar. If a platform reschedules a contest, ContestPilot automatically detects the change and updates the event instead of duplicating it.
* **Attendance Auto-Verification**: Enter your handles during setup, and ContestPilot automatically checks if you attended the contest to maintain your streak!
* **Automated Email Summaries**: Receive a beautiful "Weekly CP Report" in your inbox tracking your streak, platform breakdown, and schedule.
* **Local Background Task**: Automatically installs a silent Windows background task to run invisibly twice a day (2:00 AM and 2:00 PM) to avoid overlapping with contest hours.
* **Secure Local Database**: Uses a local SQLite database to cache history, track streaks, and prevent duplicate notifications.

## 🚀 Getting Started (Zero-Prompt Setup)

ContestPilot features a completely automated wizard. You do not need to manually install dependencies or create virtual environments.

### Prerequisites

* A Google account.

### Step 1: Install Python (Optional)

You must have Python 3.10 or higher installed on your computer. You can check your current version by opening a terminal and running:
```bash
python --version
# or
python3 --version
```
If you already have Python 3.10 or higher, you can skip this step! Otherwise, install it using the methods below:

* **Windows**: Download and install it from [python.org](https://www.python.org/downloads/). **CRITICAL**: Ensure you check the box that says **"Add python.exe to PATH"** during installation.
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

### Step 4: Get a Google App Password (For Email Alerts)

If you want ContestPilot to send you weekly email summaries, you need a special App Password. **Do not use your actual Gmail password.**
1. Ensure you have 2-Step Verification enabled on your Google Account.
2. Go to your [Google App Passwords](https://myaccount.google.com/apppasswords) page.
3. Type `ContestPilot` as the app name and click **Create**.
4. Copy the 16-character password it generates. You will paste this into the setup wizard later.

### Step 5: Setup & Run

* **Windows**: Double-click the `run.bat` file.
* **Mac / Linux**: Run `./run.sh` in your terminal.

The terminal will open, automatically create a virtual environment, install all required packages, and launch the Setup Wizard.

### The Setup Wizard
Once the app is running, the Setup Wizard will begin its 5 steps:
   * **1/5**: Automatically detects your timezone and sets up the databases.
   * **2/5**: Asks for your platform handles for auto-verification (CodeChef must be reviewed manually).
   * **3/5**: Opens a browser asking you to log into your Google Account. Click **Allow**.
   * **4/5**: Asks if you want to configure weekly Email Alerts.
   * **5/5**: Installs the silent background task (runs automatically via Windows Task Scheduler or Mac/Linux `crontab`).
It will then fetch your contests, sync your calendar, and print your personal CP Stats!

## ⚡ Quick Actions

For the best user experience, your project contains a `Quick_Actions` folder. Inside, you will find 6 easy double-click launcher files so you never have to type commands again:

(Mac/Linux users can use the equivalent `.sh` files in the same folder!)

* 🗑️ `clear_calendar.bat`: Instantly wipes all ContestPilot events from your calendar.
* 📊 `view_stats.bat`: Displays your CP Report Card and current streak.
* ⚙️ `configure_settings.bat`: Opens the wizard to update your Handles and Email preferences.
* 🛑 `uninstall_and_stop.bat`: Instantly stops all background tasks and disables email alerts.
* 🔄 `update_app.bat`: Automatically pulls the latest updates from GitHub.
* 📝 `review_contests.bat`: Asks you if you attended past CodeChef contests so you can maintain your streak.


## 🔒 Security & Privacy Notes

* **100% Local Processing**: ContestPilot runs securely on your computer. Your `contestpilot.db` (which stores your preferences and email settings), `credentials.json`, and `token.json` are automatically excluded from version control so they are never accidentally pushed to GitHub.
* **No Middleman Contest APIs**: Because it fetches data directly from the official platforms without relying on centralized third-party API keys (like clist.by), there are absolutely zero usage limits or user caps!
* ContestPilot never asks for your actual Google password. It uses standard OAuth2 tokens.
* For Email Summaries, it strictly requires a 16-character [Google App Password](https://myaccount.google.com/apppasswords), meaning your actual Gmail password is never touched.

Happy Coding! Let ContestPilot handle the schedule while you handle the algorithms.
