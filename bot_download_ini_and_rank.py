import discord
import os
import subprocess
from leaderboard_helper import post_leaderboard_dm

# === CONFIGURATION ===
TOKEN          = os.getenv("TOKEN")        # set in Railway → Variables
DOWNLOAD_FOLDER = "./records"
CHANNEL_NAME    = "lap-times"

# Ensure the records folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# === DISCORD CLIENT SETUP ===
intents = discord.Intents.default()
intents.message_content = True
intents.messages        = True
intents.guilds          = True
intents.members         = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # 📨 Send welcome message (only on truly empty DM)
    if (
        isinstance(message.channel, discord.DMChannel)
        and not message.attachments
        and not message.content.strip()
    ):
        await message.channel.send(
            "👋 **Welcome to LapTimesBot!**\n\n"
            "I'm here to help you track and rank your fastest laps in *MX Bikes*.\n\n"
            "📥 Upload your `records.ini` in this DM and I’ll reply with:\n"
            "• 🏁 A preview of your top 3 tracks\n"
            "• 📊 Your rank on every track\n"
            "• 📎 A full HTML leaderboard to download\n\n"
            "✅ Go ahead—send the file now!"
        )
        return

    # 📥 Handle INI uploads via DM or #lap-times
    if (
        (isinstance(message.channel, discord.DMChannel)
         or message.channel.name == CHANNEL_NAME)
        and message.attachments
    ):
        # ⬇️ Take ONLY the first .ini file in the message
        attachment = next(
            (a for a in message.attachments
             if a.filename.lower().endswith(".ini")),
            None
        )

        if attachment:
            player_name = message.author.name
            save_path   = os.path.join(
                DOWNLOAD_FOLDER, f"{player_name}_records.ini"
            )
            await attachment.save(save_path)
            print(f"⬇️ Saved {attachment.filename} as {save_path}")

            try:
                # Combine times
                subprocess.run(["python", "combine_lap_times.py"], check=True)
                # Send personal leaderboard DM
                await post_leaderboard_dm(player_name, message.author)

            except subprocess.CalledProcessError as e:
                await message.channel.send(f"❌ Error processing lap times: {e}")
            except discord.HTTPException as e:
                await message.channel.send(f"❌ Failed to send DM: {e}")


client.run(TOKEN)
