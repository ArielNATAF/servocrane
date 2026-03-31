import discord
import asyncio
import random
from datetime import datetime

# Import from our new modules
from config import TOKEN
import database
import api

# -- Discord Setup --
intents = discord.Intents.default()
intents.message_content = True  # Required for !register command
client = discord.Client(intents=intents)

# -- Background Loop --
async def check_news_loop():
    """Main background task that polls for new articles."""
    await client.wait_until_ready()
    
    last_post = database.get_last_post()
    first_run = True

    while not client.is_closed():
        # Anti-detection: Small jitter before fetching (1-10s)
        await asyncio.sleep(random.randint(1, 10))
        
        # Show verbose logs on first run or if it's potentially a new article
        article = api.fetch_latest_article(verbose=first_run)

        if article:
            if article["link"] != last_post:
                # If we found a new article, re-fetch with verbose=True for logging
                if not first_run:
                    api.fetch_latest_article(verbose=True)

                now = datetime.now().strftime("%H:%M:%S")
                print(f"[{now}] 🆕 Nouvelle actu : {article['title']}")

                message = (
                    f"🆕 **{article['title']}**\n"
                    f"{article['link']}"
                )

                # Send to all registered channels
                channel_ids = database.get_registered_channels()
                for c_id in channel_ids:
                    try:
                        channel = client.get_channel(c_id)
                        if channel:
                            await channel.send(message)
                    except Exception as e:
                        print(f"❌ Erreur envoi sur {c_id}: {e}")

                database.save_last_post(article["link"])
                last_post = article["link"]
            else:
                now = datetime.now().strftime("%H:%M:%S")
                print(f"[{now}] Pas de nouveauté")

        first_run = False

        # Anti-detection: Randomized sleep (4 to 7 minutes)
        sleep_time = random.randint(240, 420)
        print(f"💤 Prochain check dans {sleep_time // 60}m {sleep_time % 60}s...")
        await asyncio.sleep(sleep_time)


# -- Commands --
@client.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == client.user:
        return

    # Check for admin permissions (Manage Channels)
    if not hasattr(message.author, "guild_permissions") or not message.author.guild_permissions.manage_channels:
        return

    content = message.content.lower().strip()

    if content == "!servo-register":
        database.save_channel(message.channel.id)
        await message.channel.send("✅ **Salon enregistré !** Le bot publiera les actus Warhammer ici.")
        print(f"➕ Salon enregistré : {message.channel.name}")

    elif content == "!servo-unregister":
        database.remove_channel(message.channel.id)
        await message.channel.send("❌ **Salon retiré.** Le bot ne publiera plus ici.")
        print(f"➖ Salon retiré : {message.channel.name}")


@client.event
async def on_ready():
    print(f"🚀 Connecté en tant que {client.user}!")
    # Start background task
    client.loop.create_task(check_news_loop())


if __name__ == "__main__":
    if not TOKEN:
        print("❌ 'DISCORD_TOKEN' non trouvé dans le fichier .env")
    else:
        client.run(TOKEN)