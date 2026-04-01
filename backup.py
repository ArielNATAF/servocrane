#!/usr/bin/env python3
"""
Servo-Crane Redis Backup Script
Exports Redis state to backup/backup.json and pushes it to the 'redis-backup' git branch.

Setup (run once on the server):
  git remote set-url origin https://<YOUR_PAT>@github.com/<user>/servo-crane.git
  git checkout --orphan redis-backup
  git rm -rf .
  git commit --allow-empty -m "Init redis-backup branch"
  git push -u origin redis-backup
  git checkout main

Usage:
  python3 backup.py

Cron (daily at 3am):
  0 3 * * * /home/ubuntu/servocrane/venv/bin/python /home/ubuntu/servocrane/backup.py >> /home/ubuntu/servocrane/backup.log 2>&1
"""

import json
import os
import subprocess
from datetime import datetime, timezone

import redis
from dotenv import load_dotenv

# --- Config ---
load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "backup")
BACKUP_FILE = os.path.join(BACKUP_DIR, "backup.json")
GIT_BRANCH = "redis-backup"
REPO_DIR = os.path.dirname(__file__)


def export_redis_data(r: redis.Redis) -> dict:
    """Read all relevant keys from Redis into a dict."""
    channels = list(r.smembers("news_channels") or [])
    last_post = r.get("last_post")
    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "news_channels": sorted(channels),
        "last_post": last_post,
    }


def write_backup(data: dict):
    """Write data to the backup JSON file."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    with open(BACKUP_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[backup] Backup written to {BACKUP_FILE}")


def git(*args, cwd=REPO_DIR):
    """Run a git command and return its output."""
    result = subprocess.run(
        ["git"] + list(args),
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{result.stderr}")
    return result.stdout.strip()


def push_to_git():
    """Commit the backup file and push to the redis-backup branch."""
    # Stash current branch
    current_branch = git("rev-parse", "--abbrev-ref", "HEAD")

    try:
        # Switch to backup branch
        git("checkout", GIT_BRANCH)

        # Copy backup file into this branch's root
        root_backup = os.path.join(REPO_DIR, "backup.json")
        import shutil
        shutil.copy(BACKUP_FILE, root_backup)

        git("add", "backup.json")

        # Check if there's anything to commit
        status = git("status", "--porcelain")
        if not status:
            print("[backup] No changes detected, skipping commit.")
            return

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        git("commit", "-m", f"backup: {timestamp}")
        git("push", "origin", GIT_BRANCH)
        print(f"[backup] ✅ Pushed to branch '{GIT_BRANCH}'")

    finally:
        # Always return to the original branch
        git("checkout", current_branch)


def main():
    print(f"[backup] Starting Redis backup — {datetime.now(timezone.utc).isoformat()}")

    if not REDIS_URL:
        print("[backup] ❌ REDIS_URL not set in .env. Aborting.")
        return

    try:
        r = redis.from_url(REDIS_URL, decode_responses=True)
        r.ping()
    except Exception as e:
        print(f"[backup] ❌ Cannot connect to Redis: {e}")
        return

    data = export_redis_data(r)
    write_backup(data)
    push_to_git()
    print("[backup] Done.")


if __name__ == "__main__":
    main()
