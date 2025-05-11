import discord                     # NEW
import pandas as pd
from collections import defaultdict

EXCEL_FILE = "./records/combined_lap_records.xlsx"


async def post_leaderboard_dm(user_name, channel):
    try:
        df = pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        await channel.send("❌ Could not find lap records.")
        return

    user_tracks = df[df["Player"] == user_name]["Track"].unique()
    if not len(user_tracks):
        await channel.send("❌ You don’t have valid lap times on any ranked tracks yet.")
        return

    # Prepare HTML leaderboard
    html_lines = []
    preview = f"✅ Hey {user_name}, here's a preview of your top 3 ranked tracks:\n\n"
    track_count = 0

    for track in user_tracks:
        track_df = df[df["Track"] == track].copy()
        track_df.sort_values("Lap Time (sec)", inplace=True)
        top10 = track_df.head(10)

        # HTML section
        html_lines.append(f"<h3>{track}</h3><ol>")
        for row in top10.itertuples():
            html_lines.append(f"<li>{row.Player} — {row._4}</li>")
        html_lines.append("</ol>")

        # DM preview (first 3 tracks)
        if track_count < 3:
            preview += f"🏁 __**{track}**__\n"
            for i, row in enumerate(top10.itertuples(), 1):
                preview += f"{i}. {row.Player} — {row._4}\n"
            preview += "\n"
            track_count += 1

    html_output = "<html><body>" + "\n".join(html_lines) + "</body></html>"
    html_path = f"./records/{user_name}_leaderboard.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_output)

    try:
        await channel.send(
            preview + "\n📎 Full rankings attached as HTML.",
            file=discord.File(html_path)          # now works
        )
    except Exception as e:
        await channel.send(f"❌ Failed to send full leaderboard: {e}")
