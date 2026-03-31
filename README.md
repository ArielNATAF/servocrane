# 🤖 Warhammer Community News Bot (Servo-Crane)

A modular, high-performance Discord bot that monitors the [Warhammer Community](https://www.warhammer-community.com/) news feed and broadcasts updates to multiple channels simultaneously.

## ✨ Features

- **🚀 Real-time Monitoring**: Polling the official API with randomized intervals (4-7 mins).
- **📡 Multi-Channel Support**: Dynamically register or unregister channels using Discord commands.
- **🗄️ Hybrid Persistence**: Persistent state using **Redis** (primary) and local file fallback (secondary).
- **🛡️ Modular Architecture**: Cleanly separated logic into `api`, `database`, `config`, and `bot` modules.
- **☁️ Cloud Ready**: Optimized for 24/7 deployment on **Oracle Cloud Infrastructure (OCI)**.

## 🛠️ Project Structure

- `bot.py`: Main entry point and Discord event handlers.
- `api.py`: Warhammer Community API integration.
- `database.py`: Redis and file-based state management.
- `config.py`: Configuration and environment variables.

## ⚡ Commands

- **`!servo-register`**: Registers the current channel to receive news updates. *(Requires Manage Channels permission)*.
- **`!servo-unregister`**: Stops news updates for the current channel. *(Requires Manage Channels permission)*.

## 🚀 Setup & Deployment

### 1. Local Configuration
1.  Install dependencies: `pip install -r requirements.txt`
2.  Create a `.env` file:
    ```env
    DISCORD_TOKEN=your_token
    CHANNEL_ID=fallback_id
    REDIS_URL=redis://your-redis-url
    ```

### 2. Discord Developer Portal
- **Enable "Message Content Intent"** in the Bot settings to allow the registration commands to work.

## 📜 Dependencies

- `discord.py`: For Discord integration.
- `requests`: For fetching news data.
- `python-dotenv`: For managing secrets.
- `redis`: For cloud storage and persistence.
