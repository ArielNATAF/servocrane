import os
import random
from dotenv import load_dotenv

# Load env variables from .env file
load_dotenv()

# Discord settings
TOKEN = os.getenv("DISCORD_TOKEN")
FALLBACK_CHANNEL_ID = int(os.getenv("CHANNEL_ID")) if os.getenv("CHANNEL_ID") else None

# Redis settings
REDIS_URL = os.getenv("REDIS_URL")

# API settings
URL = "https://www.warhammer-community.com/api/search/news/"
HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://www.warhammer-community.com/en-gb/all-news-and-features/",
    "Origin": "https://www.warhammer-community.com"
}

# Payload template for API
PAYLOAD = {
    "sortBy": "date_desc",
    "category": "",
    "collections": ["articles"],
    "game_systems": [],
    "index": "news",
    "locale": "en-gb",
    "page": 0,
    "perPage": 16,
    "topics": []
}

# Anti-detection: User-Agent pool
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0"
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)
