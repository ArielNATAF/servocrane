import os
import redis
from config import REDIS_URL, FALLBACK_CHANNEL_ID

# Initialize Redis client
r = None
if REDIS_URL:
    try:
        r = redis.from_url(REDIS_URL, decode_responses=True)
        print("🗄️ Connecté à Redis pour la mémoire permanente")
    except Exception as e:
        print(f"⚠️ Erreur Redis, repli sur fichier local : {e}")

# Persistent storage file names
LAST_FILE = "last_post.txt"
CHANNELS_FILE = "channels.txt"

# --- Channel Management ---

def get_registered_channels():
    channels = set()
    
    # Load from Redis if available
    if r:
        try:
            stored_channels = r.smembers("news_channels")
            if stored_channels:
                for c_id in stored_channels:
                    channels.add(int(c_id))
        except Exception as e:
            print("Erreur chargement Redis:", e)
            
    # Load from local file as fallback
    if os.path.exists(CHANNELS_FILE):
        try:
            with open(CHANNELS_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        channels.add(int(line))
        except Exception as e:
            print("Erreur chargement fichier:", e)

    # Always include the .env channel as a fallback
    if FALLBACK_CHANNEL_ID:
        channels.add(FALLBACK_CHANNEL_ID)
        
    return list(channels)


def save_channel(channel_id):
    if r:
        try:
            r.sadd("news_channels", str(channel_id))
        except:
            pass
            
    # Also save locally for extra safety
    channels = set()
    if os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line: channels.add(line)
    
    channels.add(str(channel_id))
    with open(CHANNELS_FILE, "w") as f:
        for c_id in channels:
            f.write(f"{c_id}\n")


def remove_channel(channel_id):
    if r:
        try:
            r.srem("news_channels", str(channel_id))
        except:
            pass
            
    if os.path.exists(CHANNELS_FILE):
        channels = set()
        with open(CHANNELS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line: channels.add(line)
        
        if str(channel_id) in channels:
            channels.remove(str(channel_id))
            with open(CHANNELS_FILE, "w") as f:
                for c_id in channels:
                    f.write(f"{c_id}\n")

# --- Last Post Management ---

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
