import discord
import pandas as pd
import os
import configparser
import subprocess
from collections import defaultdict
from datetime import datetime, timezone

# === CONFIGURATION ===
import os
TOKEN = os.getenv("TOKEN")
CHANNEL_NAME = 'lap-times'
DOWNLOAD_FOLDER = "./records"
EXCEL_FILE = os.path.join(DOWNLOAD_FOLDER, 'combined_lap_records.xlsx')

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.name == CHANNEL_NAME and message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith('.ini'):
                player_name = message.author.name
                save_path = os.path.join(DOWNLOAD_FOLDER, f"{player_name}_records.ini")
                await attachment.save(save_path)
                print(f"⬇️ Saved {attachment.filename} as {save_path}")

        # === RUN YOUR SCRIPTS HERE ===
        combine_script = os.path.join(DOWNLOAD_FOLDER, "combine_lap_times.py")
        post_script = os.path.join(DOWNLOAD_FOLDER, "post_rankings_to_discord.py")

        try:
            subprocess.run(["python", combine_script], check=True)
            subprocess.run(["python", post_script], check=True)
        except subprocess.CalledProcessError as e:
            await message.channel.send(f"❌ Error running script: {e}")

def convert_seconds_to_lap_time(seconds):
    minutes = int(seconds // 60)
    remaining = seconds % 60
    return f"{minutes}'{remaining:06.3f}"

client.run(TOKEN)
