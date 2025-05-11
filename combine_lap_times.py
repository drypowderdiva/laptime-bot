import configparser
import pandas as pd
import os
from datetime import datetime, timezone

DOWNLOAD_FOLDER = "./records"
OUTPUT_FILE     = os.path.join(DOWNLOAD_FOLDER, "combined_lap_records.xlsx")

def convert_seconds_to_lap_time(seconds):
    minutes   = int(seconds // 60)
    remaining = seconds % 60
    return f"{minutes}'{remaining:06.3f}"

def read_lap_records(ini_path, player_name):
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(ini_path)

    data = []
    for track in config.sections():
        for bike, value in config[track].items():
            try:
                time_str, timestamp_str = value.strip().split()
                lap_time   = float(time_str)
                timestamp  = int(timestamp_str)
                lap_fmt    = convert_seconds_to_lap_time(lap_time)
                date_set   = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

                data.append({
                    "Player"        : player_name,
                    "Track"         : track,
                    "Bike"          : bike,
                    "Lap Time"      : lap_fmt,
                    "Lap Time (sec)": lap_time,
                    "Date Set (UTC)": date_set
                })
            except ValueError:
                continue
    return pd.DataFrame(data)

def main():
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    all_data = []

    for file in os.listdir(DOWNLOAD_FOLDER):
        if file.lower().endswith(".ini") and "records" in file.lower():
            # keep full Discord username (even with underscores)
            player_name = os.path.basename(file).rsplit("_records", 1)[0]
            ini_path    = os.path.join(DOWNLOAD_FOLDER, file)
            all_data.append(read_lap_records(ini_path, player_name))

    if not all_data:
        print("⚠️ No valid .ini lap files found.")
        return

    full_df = pd.concat(all_data, ignore_index=True)
    fastest = (full_df
               .sort_values("Lap Time (sec)")
               .groupby(["Player", "Track"], as_index=False)
               .first())

    fastest.to_excel(OUTPUT_FILE, index=False)
    print(f"✅ Combined leaderboard saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
