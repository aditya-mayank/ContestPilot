# 🚀 ContestPilot

Your ultra-lightweight, zero-config Competitive Programming assistant. ContestPilot automatically tracks upcoming coding contests from your favorite platforms, intelligently filters them based on your priorities, pushes them to your Google Calendar, and tracks your attendance streak.

## ✨ Features

- **Zero-Config Setup**: Double-click `run.bat` and you're done. No API keys, no editing files.
- **Auto-Verification**: Enter your handles and ContestPilot automatically marks your attendance!
- **Smart Filtering**: Automatically filters out contests during your busy/quiet hours.
- **Calendar Sync**: Upserts events directly to your Google Calendar with direct links.
- **Personal Coach**: Tracks your active weekly streak and provides platform breakdown stats.
- **Cloud Ready**: Includes a fully configured GitHub Actions workflow for 24/7 autonomous syncing in the cloud.

## 📥 Getting Started (Local)

1. **Clone the repository** (or download as ZIP).
2. **Double-click `run.bat`**.

That's literally it! The onboarding wizard will automatically:
- Create your database & detect your timezone.
- Prompt you to select your favorite platforms (LeetCode, Codeforces, AtCoder, etc.) and usernames.
- Open a browser to connect your Google Calendar.
- Ask if you want Email summaries or local background automation.
- Sync everything instantly.

### Advanced CLI Commands

ContestPilot runs silently, but you can interact with it at any time:
- `.\run.bat --stats` : View your current Weekly Streak, total contests attended, and platform breakdown.
- `.\run.bat --review` : Interactively review unlogged contests (for platforms without auto-verification).
- `.\run.bat --setup-email` : Configure optional daily/weekly summary emails.
- `.\run.bat --stop-all` : Completely uninstall the background scheduled task and disable emails.

## ☁️ Running in the Cloud (GitHub Actions)

ContestPilot is built to run autonomously in the cloud so you don't have to leave your PC on.

1. Run the setup wizard locally first to connect your Google Calendar.
2. Open the `token.json` file that was generated in the folder and copy its contents.
3. Fork this repository on GitHub.
4. Go to your fork's **Settings > Secrets and variables > Actions**.
5. Create a new Repository Secret named `GOOGLE_CALENDAR_TOKEN` and paste the contents of your `token.json`.

The `Daily Contest Sync` Action will now automatically run every night at midnight UTC, seamlessly pushing the latest contest updates straight to your phone's calendar!
