# 🚀 ContestPilot

**Your ultra-lightweight, fully-automated Competitive Programming assistant.**

ContestPilot is designed for competitive programmers who want to focus on solving problems rather than manually tracking schedules. It automatically fetches upcoming coding contests from your favorite platforms, filters them, pushes them to your Google Calendar, tracks your attendance streak, and even sends you weekly analytical reports—all with zero external API keys required!

---

## ✨ Why ContestPilot?

- 🚫 **Zero-Config APIs:** No Clist keys, no complex setup. ContestPilot scrapes and fetches directly from official sources.
- 📅 **Smart Calendar Sync:** Automatically upserts events directly to your Google Calendar. If a contest is rescheduled or canceled, your calendar magically updates itself.
- 📊 **CP Analytics:** Tracks your active weekly streak, total contests attended, and platform breakdown.
- 📧 **Automated Emails:** Get a "Weekly Summary" report card dropped into your inbox every week, plus instant alerts if a contest time changes suddenly.
- ☁️ **Cloud Ready:** Run it locally in the background, or deploy it to GitHub Actions for 24/7 autonomous syncing.

---

## 🌐 Supported Platforms

ContestPilot supports native fetching for the following major platforms:
- **LeetCode**
- **Codeforces**
- **CodeChef**
- **AtCoder**

---

## 📥 Getting Started (Local Setup)

We designed ContestPilot to be a "Clone, Run, and Done" experience. Follow these exact steps to get your assistant running in under 2 minutes:

### Step 1: Prerequisites
Make sure you have **Python 3** installed on your Windows machine.
1. Download Python from [python.org](https://www.python.org/downloads/).
2. **Important:** During installation, check the box that says `"Add Python to PATH"`.

### Step 2: Clone and Run
1. Clone this repository to your local machine (or download it as a ZIP and extract it).
2. Open the `ContestPilot` folder.
3. Double-click the **`run.bat`** file. 

*(Note: The first time you run this, it will automatically install all required Python libraries in a safe virtual environment.)*

### Step 3: Answer the Setup Wizard
The CLI wizard will guide you through the initial configuration:
1. **Timezone:** It will auto-detect your computer's timezone.
2. **Select Platforms:** It will ask you which platforms you want to track (e.g., LeetCode, Codeforces). Type `y` or `n`.
3. **Usernames (Optional):** Enter your handles for auto-verification of your attendance!
4. **Google Calendar Auth:** A browser window will open automatically. Sign in with your Google account and click **"Allow"** so ContestPilot can add contests to your calendar.
5. **Email Setup (Optional):** If you want weekly email reports, provide your Gmail address and a 16-character Google App Password.
6. **Background Automation:** Type `y` when asked if you want to install the background task. This allows Windows to quietly sync your contests every morning at 8:00 AM without you doing a thing.

### Step 4: Done! 🎉
ContestPilot will instantly fetch the latest contests, push them to your Google Calendar, and go to sleep. You never need to manually run `run.bat` again unless you want to check your stats!

---

## 🛠️ Advanced CLI Commands

ContestPilot runs silently in the background, but you can always interact with your data manually using the command line:

Open a terminal (Command Prompt or PowerShell) in the ContestPilot folder and run:

- `.\run.bat --stats`
  > View your personal CP Report Card! Shows your active Weekly Streak, total contests attended, missed contests, and platform breakdown.
  
- `.\run.bat --review`
  > Interactively review and mark your attendance for platforms that don't support auto-verification (like CodeChef).

- `.\run.bat --setup-email`
  > Setup or update your email credentials to receive weekly analytics.

- `.\run.bat --stop-email`
  > Instantly stop receiving automated emails.

- `.\run.bat --stop-all`
  > Completely uninstall the local Windows background task and disable all notifications.

---

## ☁️ Running in the Cloud (GitHub Actions)

Don't want to rely on your local Windows PC? ContestPilot is built to run autonomously in the cloud 24/7 for free!

1. **Run Local Setup First:** Run the setup wizard on your PC to connect your Google Calendar. This generates a `token.json` file in your folder.
2. **Fork the Repo:** Fork this ContestPilot repository to your own GitHub account.
3. **Copy Token:** Open the `token.json` file in your local folder and copy all the text inside.
4. **Add Secret:** Go to your forked repository on GitHub. Click **Settings > Secrets and variables > Actions**. Create a new Repository Secret named `GOOGLE_CALENDAR_TOKEN` and paste the text.
5. **Enable Actions:** Go to the "Actions" tab on your GitHub repository and enable workflows.

That's it! The `Daily Contest Sync` Action will now automatically run every night at midnight UTC, seamlessly pushing the latest contest updates straight to your phone's calendar, completely independent of your PC!

---

## 🔧 Troubleshooting

- **Google Calendar isn't syncing:** Delete the `token.json` file and run `.\run.bat` again to re-authenticate.
- **Emails aren't sending:** Ensure you are using a **Google App Password** (16 letters, no spaces), not your actual Gmail password. You must have 2-Factor Authentication enabled on your Google account to create an App Password.
- **Background task failing:** Ensure you ran `run.bat` from a standard folder (like Documents). Running it from restricted system folders may block the Windows Task Scheduler.

---
*Happy Coding! Let ContestPilot handle the schedule while you handle the algorithms.*
