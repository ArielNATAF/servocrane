# 🤖 Warhammer Community News Bot (Servo-Crane)

A lightweight Discord bot that monitors the [Warhammer Community](https://www.warhammer-community.com/) news feed and automatically posts updates to your server.

## ✨ Features

- **🚀 Real-time Monitoring**: Scans the official API every 4-7 minutes.
- **🕵️ Stealth Mode**: Randomized intervals, pre-fetch jitter, and User-Agent rotation to avoid detection.
- **🗄️ Permanent Memory**: Support for Upstash Redis to keep tracking news even after server restarts.
- **🛡️ Easy Deployment**: Docker-ready and optimized for free-tier hosting (Koyeb, Render, etc.).

## 🛠️ Local Setup

1. **Clone the repository** (or copy the files).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   CHANNEL_ID=your_discord_channel_id_here
   REDIS_URL=optional_upstash_redis_url  # Falls back to local file if empty
   ```
4. **Run the bot**:
   ```bash
   python bot.py
   ```

## ☁️ 24/7 Deployment (Free)

This bot is designed to run on free services like **Koyeb** or **Render**.

1. **Permanent Memory (Optional but Recommended)**:
   - Create a free database on [Upstash](https://upstash.com/).
   - Copy the Redis URL into your environment variables.
2. **Hosting**:
   - Push your code to GitHub.
   - Connect your repository to **Koyeb** or **Render**.
   - Add your `.env` variables (`DISCORD_TOKEN`, `CHANNEL_ID`, `REDIS_URL`) in the service's dashboard.
   - The bot will automatically build using the provided `Dockerfile`.

## 📜 Dependencies

- `discord.py`: For Discord integration.
- `requests`: For fetching news data.
- `python-dotenv`: For managing secrets.
- `redis`: For cloud storage.

---
