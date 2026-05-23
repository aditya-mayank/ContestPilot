# 🏆 ContestPilot

ContestPilot is a smart competitive programming assistant that fetches upcoming contests, syncs them to Google Calendar, tracks history, and sends reminders with minimal setup.

## 📌 At a Glance

**What you need to do:**
* Install Python 3.10+ (if not installed)
* Run the launcher script
* Sign in to Google once (to authorize Calendar access)
* (Optional) Enable email alerts

**What ContestPilot does automatically:**
* Detects your timezone
* Creates the local database
* Fetches contests from supported platforms
* Syncs events to your Google Calendar
* Updates calendar events if a contest is moved
* Stores your participation history
* Sends optional weekly email reminders

## 📖 About the Project

ContestPilot is a Python-based automation agent designed for Competitive Programmers. It tracks upcoming contests, pushes them directly to your Google Calendar, and maintains your participation history.

Instead of relying on third-party contest APIs like Clist.by, ContestPilot fetches contest information directly from supported platforms. The provided launcher script automatically creates a virtual environment, installs dependencies, and starts a guided wizard to get you up and running quickly.

## 🏗️ Architecture & Workflow

* **Fetchers** → Scrape and normalize contest data from supported platforms.
* **Sync Engine** → Compare, deduplicate, and update Google Calendar events.
* **Notification Layer** → Handle weekly email summaries and optional alerts.
* **Analytics Layer** → Track streaks, generate summaries, and maintain history.
* **SQLite Database** → Provide local, secure storage for user preferences and sync state.

## ✨ Key Features

* **Smart Calendar Sync**: Events are added securely to your Google Calendar. If a platform reschedules a contest, ContestPilot detects the change and updates the event.
* **Smart Reminders**: Automatically configures Google Calendar popup notifications based on contest priority (e.g., 24-hour and 1-hour warnings for major contests).
* **Direct Fetchers**: Fetches contest information directly from supported platforms without relying on centralized third-party APIs.
* **Participation Tracking**: Enter your handles during setup, and ContestPilot will help track your participation history using available platform data, with optional manual review when needed.
* **Automated Email Summaries (Optional)**: Receive a "Weekly CP Report" in your inbox tracking your streak, platform breakdown, and schedule.
* **Background Automation (Optional)**: Optionally installs a background task for automatic periodic sync on Windows, macOS, or Linux.

## 🚀 Getting Started

The launcher script handles the heavy lifting, but there are a few prerequisites.

### Step 1: Install Python 3.10+

*Skip this step only if Python 3.10+ is already installed.*

Check your version by opening a terminal and running:
```bash
python --version
# or
python3 --version
```

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
```bash
git clone https://github.com/aditya-mayank/ContestPilot.git
cd ContestPilot
```

### Step 3: Get Google Calendar Permissions

*Google Calendar access is the only required integration for core sync. It is a one-time setup required by Google so ContestPilot can add events to your calendar securely.*

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

The launcher script will create a virtual environment, install dependencies, and start the wizard automatically.

### The Guided Wizard Experience

* **Detects timezone automatically**: Ensures all calendar events are perfectly synced to your local time.
* **Enables only the platforms you want**: Tracks your handles for participation history.
* **Connects Google Calendar securely**: Opens a browser for a one-time authorization and saves the OAuth token automatically.
* **Optionally enables email alerts**: Configures your weekly summaries using the App Password.
* **Optionally installs background sync**: Sets up automatic periodic background updates so you never have to run the script manually again.

## ⚡ Quick Actions

For the best user experience, your project contains a `Quick_Actions` folder with convenient launcher scripts:

*(Mac/Linux users can use the equivalent `.sh` files in the same folder)*

* `clear_calendar` — removes all ContestPilot events
* `view_stats` — shows your current streak and history
* `configure_settings` — updates preferences
* `uninstall_and_stop` — disables automation and removes scheduled tasks
* `update_app` — pulls the latest version from GitHub
* `review_contests` — reviews contests that need manual confirmation

## 🔒 Security & Privacy

* Contest data, preferences, and history are stored locally in SQLite. 
* OAuth tokens and sensitive files (like `credentials.json`) are automatically excluded from version control.
* ContestPilot never asks for or stores your actual Google password; it uses standard OAuth2 tokens.
* Email functionality strictly uses dedicated Google App Passwords.

## ⚠️ Limitations

To remain transparent, please note the following limitations:
* Some contest platforms may change their page structure or APIs, which could temporarily break fetchers.
* Email alerts are strictly optional and depend on Gmail's App Password infrastructure.
* Attendance tracking may require manual review for platforms that lack public APIs or detailed submission histories.
* Background automation behaves slightly differently depending on your OS (Windows Task Scheduler vs. macOS/Linux `crontab`).
