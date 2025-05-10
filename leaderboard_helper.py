import pandas as pd
from collections import defaultdict

EXCEL_FILE = './records/combined_lap_records.xlsx'

async def post_leaderboard_dm(user_name, channel):
    try:
        df = pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        await channel.send("❌ Could not find lap records.")
        return

    user_tracks = df[df['Player'] == user_name]['Track'].unique()
    if not len(user_tracks):
        await channel.send("❌ You don’t have valid lap times on any ranked tracks yet.")
        return

    output = f"✅ Hey {user_name}, here are your current rankings:\n\n"

    for track in user_tracks:
        track_df = df[df['Track'] == track].copy()
        track_df.sort_values("Lap Time (sec)", inplace=True)
        top10 = track_df.head(10)

        output += f"🏁 __**{track}**__\n"
        user_in_top10 = False

        for i, row in enumerate(top10.itertuples(), 1):
            output += f"{i}. {row.Player} — {row._4}\n"
            if row.Player == user_name:
                user_in_top10 = True

        if not user_in_top10:
            user_row = track_df[track_df['Player'] == user_name].iloc[0]
            user_rank = track_df[track_df["Lap Time (sec)"] < user_row["Lap Time (sec)"]].shape[0] + 1
            output += f"...\n{user_rank}. {user_row['Player']} — {user_row['Lap Time']}\n"

        output += "\n"

    if len(output) <= 1900:
        await channel.send(output)
    else:
        for i in range(0, len(output), 1900):
            await channel.send(output[i:i+1900])
