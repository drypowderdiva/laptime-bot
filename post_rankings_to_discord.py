import discord
import pandas as pd
import os
from collections import defaultdict

# === CONFIGURATION ===
TOKEN = os.getenv("TOKEN")
CHANNEL_NAME = 'lap-times'
EXCEL_FILE = './records/combined_lap_records.xlsx'

# === DISCORD CLIENT SETUP ===
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')

    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name == CHANNEL_NAME:
                await post_leaderboard(channel)
                await client.close()
                return

    print(f"❌ Channel '{CHANNEL_NAME}' not found.")

async def post_leaderboard(channel):
    try:
        df = pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        await channel.send("❌ Excel file not found.")
        return

    # Organize and rank players by track
    leaderboard = defaultdict(list)
    for _, row in df.iterrows():
        leaderboard[row['Track']].append((row['Player'], row["Lap Time (sec)"], row["Lap Time"]))

    # Format only tracks with more than 1 unique player
    output = "**🏆 Lap Time Rankings (Tracks with Multiple Players)**\n\n"
    for track, entries in leaderboard.items():
        unique_players = set(p for p, _, _ in entries)
        if len(unique_players) < 2:
            continue  # Skip solo times

        sorted_entries = sorted(entries, key=lambda x: x[1])
        output += f"__**{track}**__\n"
        for i, (player, _, time_str) in enumerate(sorted_entries, start=1):
            output += f"{i}. {player} — {time_str}\n"
        output += "\n"

# Only send once — safely
if output.strip():  # don’t send if it's empty
    if len(output) <= 1900:
        await channel.send(output)
    else:
        chunks = [output[i:i+1900] for i in range(0, len(output), 1900)]
        for chunk in chunks:
            await channel.send(chunk)


client.run(TOKEN)

