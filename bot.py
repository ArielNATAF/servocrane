import discord
import requests
import random
import redis
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load env
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
REDIS_URL = os.getenv("REDIS_URL")

# Redis / File storage setup
r = None
if REDIS_URL:
    try:
        r = redis.from_url(REDIS_URL, decode_responses=True)
        print("🗄️ Connecté à Redis pour la mémoire permanente")
    except Exception as e:
        print(f"⚠️ Erreur Redis, repli sur fichier local : {e}")


# API config
URL = "https://www.warhammer-community.com/api/search/news/"
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

HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://www.warhammer-community.com/en-gb/all-news-and-features/",
    "Origin": "https://www.warhammer-community.com"
}

# Discord setup
intents = discord.Intents.default()
intents.message_content = False  # Set to True only if you enable it in the Discord Developer Portal
client = discord.Client(intents=intents)

# File to store last post
LAST_FILE = "last_post.txt"


def get_last_post():
    if r:
        try:
            return r.get("last_post")
        except:
            pass
    
    if not os.path.exists(LAST_FILE):
        return None
    with open(LAST_FILE, "r") as f:
        return f.read().strip()


def save_last_post(url):
    if r:
        try:
            r.set("last_post", url)
            return
        except:
            pass
            
    with open(LAST_FILE, "w") as f:
        f.write(url)


def fetch_latest_article(verbose=False):
    try:
        headers = HEADERS.copy()
        headers["User-Agent"] = random.choice(USER_AGENTS)

        res = requests.post(URL, json=PAYLOAD, headers=headers)

        if verbose:
            print("STATUS:", res.status_code)
            print("RESPONSE:", res.text[:1000])  # affiche début

        data = res.json()
        article = data["news"][0]

        title = article["title"]
        link = "https://www.warhammer-community.com" + article["uri"]
        date = article.get("date", "")

        return {
            "title": title,
            "link": link,
            "date": date
        }

    except Exception as e:
        print("Erreur API:", e)
        return None


async def check_news():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    last_post = get_last_post()
    first_run = True

    while not client.is_closed():
        # Anti-detection: Small jitter before fetching (1-10s)
        await asyncio.sleep(random.randint(1, 10))
        
        # Show logs on first run or if it's potentially a new article
        article = fetch_latest_article(verbose=first_run)

        if article:
            if article["link"] != last_post:
                # If we found a new article, re-fetch with verbose=True to show the API response in logs
                if not first_run:
                    fetch_latest_article(verbose=True)

                now = datetime.now().strftime("%H:%M:%S")
                print(f"[{now}] Nouvelle actu trouvée :", article["title"])

                message = (
                    f"🆕 **{article['title']}**\n"
                    f"{article['link']}"
                )

                await channel.send(message)
                save_last_post(article["link"])
                last_post = article["link"]  # Update variable to prevent duplicates
            else:
                now = datetime.now().strftime("%H:%M:%S")
                print(f"[{now}] Pas de nouveauté")

        first_run = False

        # Anti-detection: Randomized sleep (4 to 7 minutes)
        sleep_time = random.randint(240, 420)
        print(f"💤 Prochain check dans {sleep_time // 60}m {sleep_time % 60}s...")
        await asyncio.sleep(sleep_time)


@client.event
async def on_ready():
    print(f"Connecté en tant que {client.user}")

    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print(f"❌ Channel {CHANNEL_ID} introuvable. Vérifie que le bot a accès à ce salon.")
    else:
        print(f"✅ Channel trouvé : {channel.name}")
        await channel.send("🚀 Bot en ligne !")
        
    # Start background task
    client.loop.create_task(check_news())

client.run(TOKEN)