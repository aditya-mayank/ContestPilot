# 🏆 ContestPilot — Your Autonomous CP Scheduler & Coach
Python • Google Calendar • GitHub Actions • SQLite

Never miss a Codeforces, CodeChef, LeetCode, or AtCoder contest again — fully automated, with built-in analytics and email reports!

---

## 📌 About the Project
**ContestPilot** is a powerful Python-based automation agent designed for Competitive Programmers. It natively fetches upcoming contests from top competitive programming platforms, pushes them directly to your Google Calendar, and tracks your attendance.

Unlike traditional scripts, ContestPilot **does not require external API keys** like Clist.by. It features an interactive CLI wizard that sets up a local database, connects to your Google Calendar via OAuth, installs a silent Windows background task, and even emails you weekly CP analytical reports tracking your active streak!

---

## ✨ Key Features
- 🔄 **Native Fetchers:** Scrapes and fetches directly from official LeetCode, Codeforces, CodeChef, and AtCoder endpoints. **Zero API keys needed.**
- 📅 **Smart Google Calendar Sync:** Events are added directly to your primary calendar. If a platform reschedules a contest, ContestPilot automatically detects the change and updates the existing event.
- 🎯 **Attendance Auto-Verification:** Enter your platform handles during setup, and ContestPilot will automatically check if you attended the contest, maintaining your Weekly Streak!
- 📧 **Automated Email Summaries:** Receive a beautiful "Weekly CP Report" in your inbox tracking your streak, platform breakdown, and upcoming schedule.
- 🤖 **Local Background Task:** Includes a one-click installer to run silently in the background on Windows every morning at 8:00 AM.
- ☁️ **Cloud Ready:** Pre-configured for GitHub Actions to run 24/7 autonomously in the cloud without needing your PC.
- 🔒 **Secure Local Database:** Uses a local SQLite database (`contestpilot.db`) to cache history, track streaks, and prevent duplicate notifications.

---

## 🗂️ Project Structure
```text
ContestPilot/
├── .github/
│   └── workflows/
│       └── daily_sync.yml      # GitHub Actions workflow (runs daily)
├── contestpilot/               # Core Application Package
│   ├── analytics.py            # Calculates streaks, platform breakdowns, and attendance
│   ├── calendar_sync.py        # Handles Google Calendar OAuth & event upserts
│   ├── database.py             # SQLite wrapper for preferences and contest history
│   ├── email_sync.py           # Constructs and sends weekly/daily email reports
│   ├── fetchers.py             # Native API scrapers for LC, CF, CC, and AtCoder
│   └── utils.py                # Helpers for timezone and cache management
├── main.py                     # Entry point — orchestrates the setup wizard and sync flow
├── run.bat                     # Easy-execution batch script for Windows users
├── requirements.txt            # Python dependencies
└── .gitignore                  # Excludes databases and secrets (token.json, credentials.json)
```

---

## 🚀 Running Locally (Step-by-Step)
Follow these steps to run the project on your own machine. ContestPilot features a built-in wizard, making setup incredibly easy.

### Prerequisites
- Python 3.10 or higher
- A Google account

### Step 1 — Clone the Repository
```bash
git clone https://github.com/aditya-mayank/ContestPilot.git
cd ContestPilot
```

### Step 2 — Run the Setup Wizard
You do **not** need to manually install dependencies or create a virtual environment. ContestPilot handles this for you.

On Windows, simply double-click **`run.bat`** or run:
```bash
.\run.bat
```

The script will automatically create a virtual environment (`.venv`), install `requirements.txt`, and launch the interactive wizard.

### Step 3 — Answer the Wizard Prompts
The wizard will initialize your local SQLite database and ask:
1. Which platforms you want to track (LeetCode, Codeforces, CodeChef, AtCoder).
2. Your usernames/handles for those platforms (for Auto-Verification).
3. If you want to enable Weekly Email Alerts (requires a Gmail address and an App Password).
4. If you want to install a local Windows Scheduled Task to run silently in the background every morning.

### Step 4 — Authenticate with Google Calendar
During the wizard, a browser window will automatically open asking you to log in to your Google account.
1. Sign in and grant Calendar access.
2. A `token.json` file will be generated in your folder automatically. 
3. The script will instantly sync all upcoming contests to your calendar!

*(Note: ContestPilot requires a `credentials.json` file to identify the app to Google. If you are setting this up from scratch on a fork, see the "Google Cloud Setup" section below.)*

---

## 🛠️ Advanced CLI Commands
Once setup is complete, ContestPilot runs entirely in the background. However, you can interact with your data manually at any time:

- `.\run.bat --stats` : Generates your personal CP Report Card (Weekly Streak, Total Attended, Platform Breakdown).
- `.\run.bat --review` : Interactively review unlogged contests for platforms that don't support auto-verification.
- `.\run.bat --setup-email` : Configure optional daily/weekly summary emails.
- `.\run.bat --stop-email` : Disable email notifications.
- `.\run.bat --stop-all` : Uninstall the background scheduled task completely.

---

## ⚙️ Automating with GitHub Actions
This repo is pre-configured to run automatically every day at midnight UTC via GitHub Actions — no local machine needed!

To set it up on your own fork:
1. **Fork this repository.**
2. Run the local setup (Steps 1-4 above) on your PC to generate your `token.json` file.
3. Go to your GitHub fork → **Settings → Secrets and variables → Actions**.
4. Add the following secret:
   - **Secret Name:** `GOOGLE_CALENDAR_TOKEN`
   - **Secret Value:** Open your local `token.json` in Notepad, copy all the text, and paste it here.
5. Go to the **Actions** tab on your GitHub repo and click "Enable Workflows".

The workflow in `.github/workflows/daily_sync.yml` will now run automatically every day! ✅

---

## 🔑 Google Cloud Setup (For Forkers)
If you are forking this repo to build your own version, you will need your own Google Cloud `credentials.json` file:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Navigate to **APIs & Services → Enable APIs and Services** and enable the **Google Calendar API**.
4. Go to **OAuth consent screen**, choose **External**, fill in the details, and add the `.../auth/calendar.events` scope. Move the app to "In production".
5. Go to **Credentials → Create Credentials → OAuth Client ID** (Application type: Desktop app).
6. Download the JSON file, rename it to `credentials.json`, and place it in the root folder of ContestPilot.

---

## 🔒 Security Notes
- `credentials.json`, `token.json`, and `contestpilot.db` are excluded from version control via `.gitignore`.
- ContestPilot **never** asks for your actual Google password. It uses standard OAuth2 tokens.
- For Email Summaries, it strictly requires a 16-character [Google App Password](https://myaccount.google.com/apppasswords), meaning your actual Gmail password is never touched.
- When using GitHub Actions, all tokens are stored as encrypted GitHub Secrets.

---

## 💻 Built With
| Tech | Purpose |
|------|---------|
| **Python 3.12** | Core application logic |
| **SQLite3** | Local database for caching history & streaks |
| **Google Calendar API** | OAuth2 Calendar event management |
| **smtplib** | Email summary distribution |
| **GitHub Actions** | Autonomous cloud execution |
| **Kenkoooo API / GraphQL** | Native backend fetching |

---
*Happy Coding! Let ContestPilot handle the schedule while you handle the algorithms.*
