# 🤖 Warhammer Community News Bot (Servo-Crane)

A modular, high-performance Discord bot that monitors the [Warhammer Community](https://www.warhammer-community.com/) news feed and broadcasts updates to multiple channels simultaneously.

## ✨ Features

- **🚀 Real-time Monitoring**: Polling the official API with randomized intervals (4-7 mins).
- **📡 Multi-Channel Support**: Dynamically register or unregister channels using Discord commands.
- **🗄️ Hybrid Persistence**: Persistent state using **Redis** (primary) and local file fallback (secondary).
- **🛡️ Modular Architecture**: Cleanly separated logic into `api`, `database`, `config`, and `bot` modules.
- **☁️ Cloud Ready**: Optimized for 24/7 deployment via `systemd`.

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
    CHANNEL_ID=fallback_channel_id
    REDIS_URL=redis://your-redis-url  # optional, see below
    ```

### 2. Discord Developer Portal
- **Enable "Message Content Intent"** in the Bot settings to allow the registration commands to work.

### 3. Redis (Optional but Recommended)

Redis stores the list of registered channels persistently. Without it, the bot uses local `.txt` files.

**Install Redis on your server (Ubuntu):**
```bash
sudo apt update
sudo apt install redis-server -y
```

**Enable and start the Redis service:**
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

**Verify Redis is running:**
```bash
sudo systemctl status redis-server
# or test the connection:
redis-cli ping
# Expected output: PONG
```

**Configure `.env` to use local Redis:**
```env
REDIS_URL=redis://localhost:6379
```

### 4. Running as a 24/7 System Service (systemd)

`systemd` is the Linux service manager that runs your bot automatically on startup and restarts it if it crashes.

**Create the service file:**
```bash
sudo nano /etc/systemd/system/servocrane.service
```

**Paste this configuration:**
```ini
[Unit]
Description=Servo-Crane Discord Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/servocrane
ExecStart=/home/ubuntu/servocrane/venv/bin/python -u bot.py
# -u = unbuffered: forces logs to appear immediately in journalctl
Restart=always
RestartSec=10
EnvironmentFile=/home/ubuntu/servocrane/.env

[Install]
WantedBy=multi-user.target
```

**Enable and start the service:**
```bash
sudo systemctl daemon-reload        # Reload systemd to pick up the new file
sudo systemctl enable servocrane    # Auto-start on boot
sudo systemctl start servocrane     # Start it now
```

**Useful systemd commands:**

| Command | Description |
|---|---|
| `sudo systemctl status servocrane` | Check if the bot is running |
| `sudo systemctl start servocrane` | Start the bot |
| `sudo systemctl stop servocrane` | Stop the bot |
| `sudo systemctl restart servocrane` | Restart after a code update |
| `sudo journalctl -u servocrane -f` | Watch live logs |
| `sudo journalctl -u servocrane -n 100` | View last 100 log lines |

**Updating the bot after a `git pull`:**
```bash
git pull
sudo systemctl restart servocrane
```

### 5. Redis Backup (Automatic, Daily)

`backup.py` exports Redis state (`news_channels`, `last_post`) to `backup.json` and pushes it to an orphan `redis-backup` git branch. This runs automatically every night via cron.

**One-time setup (on the server):**
```bash
# Authenticate git with a GitHub Personal Access Token (PAT with 'repo' scope)
git remote set-url origin https://<YOUR_PAT>@github.com/<youruser>/servo-crane.git

# Create the orphan backup branch (no shared history with main)
git checkout --orphan redis-backup
git rm -rf .
git commit --allow-empty -m "Init redis-backup branch"
git push -u origin redis-backup
git checkout main
```

**Test manually:**
```bash
python3 backup.py
```

**Schedule with cron (runs daily at 3am):**
```bash
crontab -e
```
Add this line:
```
0 3 * * * /home/ubuntu/servocrane/venv/bin/python /home/ubuntu/servocrane/backup.py >> /home/ubuntu/servocrane/backup.log 2>&1
```

> Cron runs independently of your SSH session — it keeps running even when you are disconnected.

**Check backup logs:**
```bash
cat ~/servocrane/backup.log
```

## 📜 Dependencies

- `discord.py`: For Discord integration.
- `requests`: For fetching news data.
- `python-dotenv`: For managing configuration.
- `redis`: For cloud storage and persistence.
