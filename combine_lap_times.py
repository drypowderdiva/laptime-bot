import configparser
import pandas as pd
import os
from datetime import datetime, timezone

# Use a local folder for Railway or any cloud host
DOWNLOAD_FOLDER = "./records"
OUTPUT_FILE = os.path.join(DOWNLOAD_FOLDER, "combined_lap_records.xlsx")

def convert_seconds_to_lap_time(seconds):
    minutes = int(seconds // 60)
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
                lap_time = float(time_str)
                timestamp = int(timestamp_str)
                lap_formatted = convert_seconds_to_lap_time(lap_time)
                date_set = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

                data.append({
                    "Player": player_name,
                    "Track": track,
                    "Bike": bike,
                    "Lap Time": lap_formatted,
                    "Lap Time (sec)": lap_time,
                    "Date Set (UTC)": date_set
                })
            except ValueError:
                continue

    return pd.DataFrame(data)

def main():
    all_data = []

    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    for file in os.listdir(DOWNLOAD_FOLDER):
        if file.endswith(".ini") and "records" in file.lower():
            ini_path = os.path.join(DOWNLOAD_FOLDER, file)
            player_name = file.split("_")[0]
            df = read_lap_records(ini_path, player_name)
            all_data.append(df)

    if not all_data:
        print("⚠️ No valid .ini lap files found.")
        return

    full_df = pd.concat(all_data, ignore_index=True)

    fastest_per_track = full_df.sort_values("Lap Time (sec)").groupby(["Player", "Track"], as_index=False).first()

    fastest_per_track.to_excel(OUTPUT_FILE, index=False)
    print(f"✅ Combined leaderboard saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
    
