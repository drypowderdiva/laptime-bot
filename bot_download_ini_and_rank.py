import discord
import pandas as pd
import os
from collections import defaultdict
from leaderboard_helper import post_leaderboard_dm

# === CONFIGURATION ===
TOKEN = os.getenv("TOKEN")  # ✅ secure for cloud deployment
CHANNEL_NAME = 'lap-times'
EXCEL_FILE = './records/combined_lap_records.xlsx'  # ✅ cloud-safe path

# === DISCORD CLIENT SETUP ===
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')

async def post_leaderboard(channel):
    try:
        df = pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        await post_leaderboard_dm(user.name, dm_channel)
        return

    leaderboard = defaultdict(list)
    for _, row in df.iterrows():
        leaderboard[row['Track']].append((row['Player'], row["Lap Time (sec)"], row["Lap Time"]))

    output = "**🏆 Lap Time Rankings (Tracks with Multiple Players)**\n\n"
    for track, entries in leaderboard.items():
        unique_players = set(p for p, _, _ in entries)
        if len(unique_players) < 2:
            continue

        sorted_entries = sorted(entries, key=lambda x: x[1])
        output += f"__**{track}**__\n"
        for i, (player, _, time_str) in enumerate(sorted_entries, start=1):
            output += f"{i}. {player} — {time_str}\n"
        output += "\n"

    if output.strip():
        if len(output) <= 1900:
            await channel.send(output)
        else:
            for i in range(0, len(output), 1900):
                await channel.send(output[i:i+1900])

client.run(TOKEN)
