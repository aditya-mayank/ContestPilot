# 📘 ContestPilot: Comprehensive Project Explanation

This document serves as the master architectural reference and interview guide for ContestPilot. It explains the philosophy, design decisions, data flow, and codebase structure in extreme detail.

---

## 🚀 Project Overview

**ContestPilot** is a smart, autonomous competitive programming assistant. At its core, it solves a very specific problem: *Competitive programmers frequently miss contests because tracking schedules across multiple platforms is tedious.*

Instead of requiring users to manually check websites or rely on third-party aggregators that often have rate limits or delayed updates, ContestPilot:
1. Scrapes official endpoints directly to find upcoming contests.
2. Normalizes that data and stores it in a local database.
3. Syncs those contests to the user's personal Google Calendar.
4. Tracks participation history and sends optional weekly email reports.
5. Runs entirely in the background via automated OS schedulers.

**Why is this better than a simple script?**
A simple python script requires the user to remember to run it. It lacks state (meaning it would blindly create duplicate events on the calendar every time it runs). ContestPilot acts as a true *stateful agent*: it runs invisibly on a schedule, remembers what it has already synced, cleanly handles when platforms reschedule a contest, and maintains a historical database of the user's analytics.

---

## 🛠️ Why This Tech Stack Was Chosen

### Why Python?
Python is the undisputed king of scripting, data scraping, and automation. It has mature, battle-tested libraries for web scraping (`BeautifulSoup`), API interaction (`requests`), Google Calendar integration (`google-api-python-client`), and timezone manipulation (`pytz`, `tzlocal`). Because this is a desktop utility meant for developers, Python allows the code to remain readable and highly extensible.

### Why SQLite instead of PostgreSQL/MySQL?
ContestPilot is designed as a **local-first, zero-setup desktop application**, not a web server. 
- **Zero Configuration:** SQLite requires no installation, no background daemon, and no user setup. It's just a file (`contestpilot.db`).
- **Portability:** If a user wants to back up their data or move to a new computer, they literally just copy the `.db` file.
- **Scale:** A single user tracking their contest history generates a few kilobytes of data a year. A full RDBMS like PostgreSQL is massive overkill and would ruin the "one-click setup" experience.

### Why Google Calendar?
Developers already live by their calendars. Instead of forcing the user to open a custom GUI to see upcoming contests, pushing the events directly to the tool they already check daily (and syncs to their phone) guarantees they won't miss a contest. Google Calendar is universally adopted and its API supports deep customization (like overriding popup reminders based on contest priority).

---

## 🏗️ Architecture

ContestPilot uses a modular, decoupled architecture. 

1. **The Core (`main.py`)**: The conductor. It handles the initial setup wizard, parses command-line arguments, and triggers the other modules.
2. **The Data Layer (`database.py`, `models.py`)**: Manages the SQLite connection, schema initialization, and basic CRUD operations.
3. **The Ingestion Layer (`fetchers.py`)**: Responsible for reaching out to the internet, grabbing raw JSON/HTML, and returning a standardized Python dictionary.
4. **The Integration Layer (`calendar_sync.py`)**: Converts the standardized Python dictionary into Google Calendar API payloads and pushes them.
5. **The Analytics & Notification Layer (`analytics.py`, `attendance_verifier.py`, `email_sync.py`)**: Post-contest logic. Checks if the user attended, updates the DB streak, and formats/sends the weekly email.

---

## 📂 File-by-File Explanation

* `main.py`: The entry point. Handles the setup wizard, OS detection for background jobs, and the primary execution loop.
* `contestpilot/database.py`: Handles SQLite connections. It creates tables if they don't exist and manages user preferences.
* `contestpilot/fetchers.py`: Contains individual classes (e.g., `LeetCodeFetcher`, `CodeforcesFetcher`). **Why separate them?** Because if Codeforces changes their API tomorrow, only the `CodeforcesFetcher` breaks. The rest of the app continues working perfectly.
* `contestpilot/calendar_sync.py`: Handles Google OAuth authentication and the `insert`/`update` logic for Calendar events.
* `contestpilot/attendance_verifier.py`: Scrapes a user's public profile on the platforms to check if they submitted code during a specific contest timeframe.
* `contestpilot/analytics.py`: Generates the "CP Report Card" in the terminal (streak calculation, win rate, etc).
* `contestpilot/email_sync.py` & `setup_email.py`: Compiles the analytics into an HTML email and sends it via SMTP.
* `contestpilot/utils.py`: Helper functions, specifically complex timezone conversion logic.
* `run.bat` & `run.sh`: The user-facing launcher scripts. **Why are they needed?** They abstract away the complexity of Python virtual environments so the user just double-clicks to start.
* `Quick_Actions/`: A folder of tiny scripts that just call `run.bat --[flag]`. **Why?** To give users a GUI-like experience without building an actual GUI.

---

## 🔄 Data Flow

1. **Fetch**: `sync_all_fetchers()` calls each platform fetcher. The fetchers hit endpoints, parse data, and yield raw contest objects.
2. **Normalize**: Fetchers convert differing platform formats into a strict, unified dictionary structure.
3. **Store**: `database.py` receives the normalized dictionary. It checks if the `contest_id` exists. If not, it inserts it. If it does, it *updates* it (this handles reschedules).
4. **Rank**: The system applies priority logic (e.g., "Div 1" contests might get HIGH priority, "Div 4" might get LOW).
5. **Sync**: `calendar_sync.py` queries the database for *upcoming* contests. It generates a deterministic event ID, connects to Google Calendar, and attempts to insert the event. If a `409 Conflict` occurs (meaning the event already exists), it issues an `update` request instead, ensuring the calendar perfectly matches the database.
6. **Post-Contest**: Days later, `attendance_verifier.py` checks past contests in the DB, queries the platform's user profile, and updates the DB row to `ATTENDED` or `MISSED`.

---

## 🧑‍💻 User Flow (The Setup Wizard)

**Why is the setup wizard designed this way?**
Developers hate configuring boilerplate. The wizard is designed to capture everything necessary in a single, guided, 30-second flow so they never have to touch a configuration file.

1. **Launcher**: User runs `run.bat`. It builds the isolated Python environment automatically.
2. **Timezone**: Detected automatically from the OS. No manual input required.
3. **Handles**: Asks for usernames for the attendance tracking feature.
4. **Calendar Auth**: Opens a browser. The user clicks "Allow". The token is saved.
5. **Automation**: The script detects if it's on Windows, Mac, or Linux and silently injects a `crontab` or `Scheduled Task`. 
6. **Result**: The app goes to sleep. The user never has to run it again.

---

## 🧠 Important Design Decisions

### Why use OAuth instead of asking for Google passwords?
Security and trust. Asking for a user's Google password is a massive red flag and often blocked by Google's modern security policies anyway. OAuth redirects the user to Google's official login page. Google then returns a secure `token.json` that *only* grants permission to edit the calendar, nothing else.

### Why use UTC internally?
Time is incredibly difficult to manage in programming because of Daylight Saving Time, leap years, and regional timezone changes. **Rule of thumb:** *Always store time in UTC in the database, and only convert to local time when showing it to the user.* 
If a user travels from New York to Tokyo, their local time changes, but UTC remains absolute. By storing contests in UTC, the database never breaks.

### Why do we need timezone conversion?
Platforms serve API data in different formats. Codeforces serves Unix timestamps (UTC). LeetCode might serve Pacific Time. AtCoder might serve Japan Standard Time. The fetchers *must* convert these varying formats into absolute UTC before saving to the database so the `calendar_sync` module has a reliable, unified source of truth.

### Why are contests normalized before syncing?
If every platform returned a different data structure, the Calendar sync code would need massive, messy `if/else` blocks (`if platform == 'leetcode': do_this()`). By forcing all fetchers to return a standardized `Contest` model, the Calendar module can be completely "dumb"—it just loops through a list of identical objects and pushes them.

### Why is duplicate prevention needed?
If the script runs twice a day, and it blindly pushed events to Google Calendar, the user would end up with 14 identical events for the same contest in a week. 

### How is duplicate prevention / reschedule detection handled?
The secret is in `make_stable_event_id()`. Google Calendar requires event IDs to be unique base32hex strings. ContestPilot takes the unique ID from the platform (e.g., `codeforces_1955`), hashes it into a valid Google Event ID, and pushes it. 
When it pushes, if Google responds with a `409 Conflict` (meaning "I already have an event with this ID!"), ContestPilot catches the error and says, "Great, then *update* the existing event with this new data." This inherently solves both duplicates and rescheduled contests!

### Why are email and WhatsApp optional?
Not everyone wants a cluttered inbox, and setting up an App Password adds friction. WhatsApp integration requires paid Twilio APIs or unstable web-scraping wrappers, making it too brittle for a core feature. Keeping these optional ensures the core product (Calendar sync) remains frictionless.

---

## ⚠️ Edge Cases and Limitations

1. **Scraping Fragility**: "Direct Fetchers" is a double-edged sword. While it removes the need for third-party API keys, if a platform like CodeChef completely rewrites their website HTML, the `BeautifulSoup` scraper will break. This requires the developer to push an update.
2. **Attendance Verification Limits**: Not all platforms have public submission histories. For platforms without public APIs, attendance tracking falls back to the manual `review_contests.bat` script.
3. **App Passwords**: The email feature relies on Gmail App Passwords, which Google occasionally hides deep in their security settings, confusing less technical users.
4. **Background Schedulers**: Windows Task Scheduler and Unix `crontab` behave differently. If a Mac user puts their laptop to sleep at exactly 2:00 PM, `crontab` might skip the execution entirely, delaying the sync until the 2:00 AM run.

---

## 🛡️ Security Choices

* **.gitignore**: The `contestpilot.db`, `credentials.json`, and `token.json` files contain the user's private life (handles, OAuth tokens, email passwords). They are strictly excluded from git so a user can't accidentally push their secrets to GitHub.
* **Local Storage**: Storing the DB locally means there is no central ContestPilot server that could be hacked to steal user schedules. The user owns their data 100%.

---

## 🤝 New Contributor Guide

**How to extend the code (e.g., adding a new platform like HackerRank):**
1. Open `fetchers.py`.
2. Create a `HackerRankFetcher(BaseFetcher)` class.
3. Implement the `fetch()` method. Make a network request, parse the data, and `yield` a dictionary containing `id`, `name`, `url`, `start_time`, and `end_time` (ensuring times are converted to UTC!).
4. Add the fetcher to the `get_all_fetchers()` list at the bottom of the file.
5. That's it! The database, calendar sync, and analytics will automatically start supporting HackerRank.

---

## 💼 Interview Explanation & Summaries

### Short Summary (Elevator Pitch)
"ContestPilot is a local-first Python automation agent that scrapes competitive programming schedules, syncs them to Google Calendar, and tracks user attendance entirely in the background."

### Medium Summary (For GitHub / Resume)
"ContestPilot is an autonomous competitive programming assistant built in Python. Utilizing an extensible architecture, it fetches upcoming contests directly from platforms like Codeforces and LeetCode, normalizes the data into a local SQLite database, and securely syncs events to Google Calendar via OAuth2. It features a zero-configuration setup wizard, OS-native background scheduling (crontab/Task Scheduler), and automated attendance tracking with email reporting."

### Top 10 Things to Know for an Interview
1. **The Architecture**: It's modular. Fetchers (Ingestion) -> SQLite (Storage) -> Calendar (Integration).
2. **Data Normalization**: Why fetchers convert varying API data into a single strict schema.
3. **Idempotency**: The calendar sync is *idempotent*. Running it 1 time or 100 times results in the exact same calendar state (via stable Event IDs).
4. **Timezone Handling**: Always store in UTC, display in local time.
5. **OAuth2 Flow**: Why it's used over password authentication for Google Calendar.
6. **Local-First Design**: Why SQLite was chosen over Postgres (portability, zero-config).
7. **Cross-Platform Automation**: How Python interacts with the underlying OS (Windows `schtasks` vs Unix `crontab`).
8. **Reschedule Detection**: How catching `409 Conflict` errors allows the app to cleanly update moved contests.
9. **Extensibility**: How the `BaseFetcher` pattern allows new platforms to be added in minutes without touching core logic.
10. **Tradeoffs**: Being honest about the fragility of web scraping vs. relying on third-party APIs like Clist.

---

## ❓ FAQ

**Q: Why not just use Clist.by?**
A: Clist is fantastic, but relying on a central API creates a single point of failure and subjects users to rate limits. Direct fetching ensures autonomy.

**Q: Will it drain my battery?**
A: No. The script sleeps 99.9% of the time and only wakes up twice a day, runs for ~3 seconds, and closes.

**Q: What happens if a contest gets canceled?**
A: The fetcher will pick up the cancellation flag, save it to the DB, and the Calendar sync will prepend `[CANCELED]` to the Google Calendar event title.
