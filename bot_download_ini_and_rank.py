import discord
import pandas as pd
import os
import subprocess
from leaderboard_helper import post_leaderboard_dm

# === CONFIGURATION ===
TOKEN = os.getenv("TOKEN")
DOWNLOAD_FOLDER = "./records"
EXCEL_FILE = './records/combined_lap_records.xlsx'
CHANNEL_NAME = 'lap-times'

# Make sure records folder exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# === DISCORD CLIENT SETUP ===
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Accept files via DM or in #lap-times
    if (isinstance(message.channel, discord.DMChannel) or message.channel.name == CHANNEL_NAME) and message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith('.ini'):
                player_name = message.author.name
                save_path = os.path.join(DOWNLOAD_FOLDER, f"{player_name}_records.ini")
                await attachment.save(save_path)
                print(f"⬇️ Saved {attachment.filename} as {save_path}")

                try:
                    subprocess.run(["python", "combine_lap_times.py"], check=True)
                    dm_channel = await message.author.create_dm()
                    await post_leaderboard_dm(player_name, dm_channel)
                except subprocess.CalledProcessError as e:
                    await message.channel.send(f"❌ Error processing lap times: {e}")

client.run(TOKEN)
