import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
from datetime import datetime

# Import from our new modules
from config import TOKEN
import database
import api

# -- Global Bot State --
bot_start_time = datetime.now()
last_query_time = None
user_cooldowns = {}  # Tracks last command time per user

# -- Discord Setup --
intents = discord.Intents.default()
intents.message_content = True  # Required for !register command
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# -- Background Loop --
async def check_news_loop():
    """Main background task that polls for new articles."""
    await bot.wait_until_ready()
    
    last_post = database.get_last_post()
    first_run = True

    while not bot.is_closed():
        # Anti-detection: Small jitter before fetching (1-10s)
        await asyncio.sleep(random.randint(1, 10))
        
        global last_query_time
        last_query_time = datetime.now()
        
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
                        channel = bot.get_channel(c_id)
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

        # Anti-detection: Randomized sleep (10 to 20 minutes)
        sleep_time = random.randint(600, 1200)
        # print(f"💤 Prochain check dans {sleep_time // 60}m {sleep_time % 60}s...")
        await asyncio.sleep(sleep_time)


# -- Commands --
@bot.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == bot.user:
        return

    # Check for admin permissions (Manage Channels)
    if not hasattr(message.author, "guild_permissions") or not message.author.guild_permissions.manage_channels:
        return

    content = message.content.lower().strip()
    
    # Anti-spam: check cooldown (5 seconds)
    if content.startswith("!servo-"):
        user_id = message.author.id
        now = datetime.now().timestamp()
        last_time = user_cooldowns.get(user_id, 0)
        
        if now - last_time < 5:
            # Optionally add a silent ignore or a small reaction
            # print(f"⏳ Anti-spam: {message.author} ignoré")
            return
        
        user_cooldowns[user_id] = now

    if content == "!servo-register":
        database.save_channel(message.channel.id)
        await message.channel.send("✅ **Salon enregistré !** Le bot publiera les actus Warhammer ici.")
        print(f"➕ Salon enregistré : {message.channel.name}")

    elif content == "!servo-unregister":
        database.remove_channel(message.channel.id)
        await message.channel.send("❌ **Salon retiré.** Le bot ne publiera plus ici.")
        print(f"➖ Salon retiré : {message.channel.name}")

    elif content == "!servo-status":
        uptime = datetime.now() - bot_start_time
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        last_post_link = database.get_last_post() or "Aucun"
        channels_count = len(database.get_registered_channels())
        
        last_query_str = last_query_time.strftime("%d/%m/%Y %H:%M:%S") if last_query_time else "Jamais"
        ping_ms = round(bot.latency * 1000)
        
        status_msg = (
            "📊 **Status du Servo-Crane** 📊\n"
            f"**Uptime :** `{uptime_str}`\n"
            f"**Dernière vérification :** `{last_query_str}`\n"
            f"**Dernier article posté :** {last_post_link}\n"
            f"**Salons abonnés :** `{channels_count}`\n"
            f"**Ping :** `{ping_ms}ms`"
        )
        await message.channel.send(status_msg)
        print(f"📊 Status demandé par {message.author} dans {message.channel.name}")


# -- Slash Commands --
@bot.tree.command(name="servo-register", description="Enregistre un salon pour recevoir les actus Warhammer")
@app_commands.describe(channel="Le salon où les news seront postées (optionnel, par défaut celui-ci)")
@app_commands.checks.has_permissions(manage_channels=True)
async def servo_register(interaction: discord.Interaction, channel: discord.TextChannel = None):
    # If no channel is provided, use the current channel
    target_channel = channel or interaction.channel
    
    database.save_channel(target_channel.id)
    await interaction.response.send_message(f"✅ **Salon enregistré !** Le bot publiera les actus Warhammer dans {target_channel.mention}.")
    print(f"➕ Salon enregistré via slash: {target_channel.name}")

@bot.tree.command(name="servo-unregister", description="Retire un salon de la liste des abonnés")
@app_commands.describe(channel="Le salon à retirer (optionnel, par défaut celui-ci)")
@app_commands.checks.has_permissions(manage_channels=True)
async def servo_unregister(interaction: discord.Interaction, channel: discord.TextChannel = None):
    target_channel = channel or interaction.channel
    database.remove_channel(target_channel.id)
    await interaction.response.send_message(f"❌ **Salon retiré.** Le bot ne publiera plus dans {target_channel.mention}.")
    print(f"➖ Salon retiré via slash: {target_channel.name}")

@bot.tree.command(name="servo-status", description="Affiche les statistiques et l'état du bot")
async def servo_status(interaction: discord.Interaction):
    uptime = datetime.now() - bot_start_time
    uptime_str = str(uptime).split('.')[0]
    
    last_post_link = database.get_last_post() or "Aucun"
    channels_count = len(database.get_registered_channels())
    
    last_query_str = last_query_time.strftime("%d/%m/%Y %H:%M:%S") if last_query_time else "Jamais"
    ping_ms = round(bot.latency * 1000)
    
    status_msg = (
        "📊 **Status du Servo-Crane** 📊\n"
        f"**Uptime :** `{uptime_str}`\n"
        f"**Dernière vérification :** `{last_query_str}`\n"
        f"**Dernier article posté :** {last_post_link}\n"
        f"**Salons abonnés :** `{channels_count}`\n"
        f"**Ping :** `{ping_ms}ms`"
    )
    await interaction.response.send_message(status_msg)
    print(f"📊 Status demandé via slash par {interaction.user} dans {interaction.channel.name}")

@servo_register.error
@servo_unregister.error
async def slash_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ Tu n'as pas la permission `Gérer les salons` pour utiliser cette commande.", ephemeral=True)
    else:
        # Check if already responded to avoid double response errors
        if not interaction.response.is_done():
            await interaction.response.send_message(f"❌ Une erreur est survenue : {error}", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Une erreur est survenue : {error}", ephemeral=True)


@bot.event
async def on_ready():
    print(f"🚀 Connecté en tant que {bot.user}!")
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"🔄 {len(synced)} commandes slash synchronisées.")
    except Exception as e:
        print(f"❌ Erreur de synchro slash: {e}")

    # Start background task
    bot.loop.create_task(check_news_loop())


if __name__ == "__main__":
    if not TOKEN:
        print("❌ 'DISCORD_TOKEN' non trouvé dans le fichier .env")
    else:
        bot.run(TOKEN)