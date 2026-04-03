# 🤖 Warhammer Community News Bot (Servo-Crane)

A modular, high-performance Discord bot that monitors the [Warhammer Community](https://www.warhammer-community.com/) news feed and broadcasts updates to multiple channels simultaneously.

## ✨ Features

- **🚀 Real-time Monitoring**: Polling the official API with randomized intervals (10-20 mins).
- **📡 Multi-Channel Support**: Dynamically register or unregister channels using **Slash Commands** or prefix commands.
- **🗄️ Hybrid Persistence**: Persistent state using **Redis** (primary) and local file fallback (secondary).
- **🛡️ Modern Interface**: Supports Discord Slash Commands with optional parameters for targeted channel management.
- **☁️ Cloud Ready**: Optimized for 24/7 deployment via `systemd`.

## 🛠️ Project Structure

- `bot.py`: Main entry point and Discord event handlers.
- `api.py`: Warhammer Community API integration.
- `database.py`: Redis and file-based state management.
- `config.py`: Configuration and environment variables.

## ⚡ Commands

### Slash Commands (Recommended)
- **`/servo-register`**: Registers a channel for news updates.
    - `channel` (optional): Specify a different channel to register.
- **`/servo-unregister`**: Stops news updates for a channel.
    - `channel` (optional): Specify a different channel to unregister.
- **`/servo-status`**: Get the bot status, uptime, and last query time.

### Legacy Prefix Commands
- **`!servo-register`**: Registers the current channel.
- **`!servo-unregister`**: Unregisters the current channel.
- **`!servo-status`**: Get diagnostic information.

> [!NOTE]
> All admin commands require the **Manage Channels** permission.

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
- **Enable "Message Content Intent"** in the Bot settings to allow the prefix commands to work.
- **OAuth2 Scopes**: Ensure the bot is invited with the `applications.commands` scope (in addition to `bot`).

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

### 6. Securing your Oracle Cloud VPS (Fail2ban)

Since your server has an open SSH port, it's highly recommended to install `fail2ban` to protect it against brute-force attacks by automatically blocking malicious IP addresses.

**Install Fail2ban:**
```bash
sudo apt update
sudo apt install fail2ban -y
```

**Configure Fail2ban:**
Fail2ban works out of the box for SSH, but it's best practice to create a local configuration file so updates don't overwrite your settings:
```bash
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
```
*(Optional) You can edit `/etc/fail2ban/jail.local` to adjust the `bantime` or `maxretry` limits.*

**Start and Enable the Service:**
```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

**Verify Fail2ban is working:**
```bash
sudo systemctl status fail2ban
# See the number of currently banned IPs:
sudo fail2ban-client status sshd
```

## 📜 Dependencies

- `discord.py`: For Discord integration.
- `requests`: For fetching news data.
- `python-dotenv`: For managing configuration.
- `redis`: For cloud storage and persistence.
