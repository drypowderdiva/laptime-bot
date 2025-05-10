import discord
import pandas as pd
import os
import subprocess
from leaderboard_helper import post_leaderboard_dm

# === CONFIGURATION ===
TOKEN = os.getenv("TOKEN")
DOWNLOAD_FOLDER = "./records"
CHANNEL_NAME = 'lap-times'

# Ensure records folder exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# === DISCORD CLIENT SETUP ===
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Accept INI file via DM or in #lap-times channel
    if (isinstance(message.channel, discord.DMChannel) or message.channel.name == CHANNEL_NAME) and message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith('.ini'):
                player_name = message.author.name
                save_path = os.path.join(DOWNLOAD_FOLDER, f"{player_name}_records.ini")
                await attachment.save(save_path)
                print(f"⬇️ Saved {attachment.filename} as {save_path}")

                try:
                    # ✅ Only run the combiner
                    subprocess.run(["python", "combine_lap_times.py"], check=True)

                    # ✅ Send DM using helper function (only once)
                    await post_leaderboard_dm(player_name, message.author)

                except subprocess.CalledProcessError as e:
                    await message.channel.send(f"❌ Error processing lap times: {e}")
                except discord.HTTPException as e:
                    await message.channel.send(f"❌ Failed to send DM: {e}")

client.run(TOKEN)
