import os
import re
import pandas as pd
import numpy as np
import json
from scipy.interpolate import interp1d
from glob import glob

# Expected frequencies for each sensor
expected_rates = {
    "EDA": 15,
    "PPG": 25,
    "Temperature": 7.5,
    "Motion": 25
}

# ---------- Helpers ----------
def expand_data(df, expected_rates):
    eda_data, ppg_data, temp_data, motion_data = [], [], [], []

    for _, row in df.iterrows():
        timestamp = row["ts"]  # Base timestamp
        
        try:
            sensor_data = json.loads(row["data"])
        except json.JSONDecodeError:
            continue  # Skip rows with corrupted JSON

        # EDA
        if "eda" in sensor_data:
            interval = 1 / expected_rates["EDA"]
            times = [timestamp + (interval * i) for i in range(len(sensor_data["eda"]))]
            for ts, eda, edl in zip(
                times,
                sensor_data["eda"],
                sensor_data.get("edl", [None] * len(sensor_data["eda"]))
            ):
                eda_data.append({
                    "timestamp": ts,
                    "EDA": round(eda, 2),
                    "EDL": round(edl, 2) if edl is not None else None
                })

        # PPG
        if "pgi" in sensor_data:
            interval = 1 / expected_rates["PPG"]
            times = [timestamp + (interval * i) for i in range(len(sensor_data["pgi"]))]
            for ts, pgi, pgr, pgg in zip(
                times,
                sensor_data["pgi"],
                sensor_data.get("pgr", [None] * len(sensor_data["pgi"])),
                sensor_data.get("pgg", [None] * len(sensor_data["pgi"]))
            ):
                ppg_data.append({
                    "timestamp": ts,
                    "PI": round(pgi, 2),
                    "PR": round(pgr, 2) if pgr is not None else None,
                    "PG": round(pgg, 2) if pgg is not None else None
                })

        # Temperature
        if "thr" in sensor_data:
            interval = 1 / expected_rates["Temperature"]
            times = [timestamp + (interval * i) for i in range(len(sensor_data["thr"]))]
            for ts, thr in zip(times, sensor_data["thr"]):
                temp_data.append({"timestamp": ts, "Temp": round(thr, 2)})

        # Motion
        if "acx" in sensor_data:
            interval = 1 / expected_rates["Motion"]
            times = [timestamp + (interval * i) for i in range(len(sensor_data["acx"]))]
            for ts, acx, acy, acz, gyx, gyy, gyz, mgx, mgy, mgz in zip(
                times,
                sensor_data["acx"], sensor_data["acy"], sensor_data["acz"],
                sensor_data["gyx"], sensor_data["gyy"], sensor_data["gyz"],
                sensor_data["mgx"], sensor_data["mgy"], sensor_data["mgz"]
            ):
                motion_data.append({
                    "timestamp": ts,
                    "ACC_x": round(acx, 2), "ACC_y": round(acy, 2), "ACC_z": round(acz, 2),
                    "GY_x": round(gyx, 2),  "GY_y": round(gyy, 2),  "GY_z": round(gyz, 2),
                    "MG_x": round(mgx, 2),  "MG_y": round(mgy, 2),  "MG_z": round(mgz, 2)
                })
    
    return eda_data, ppg_data, temp_data, motion_data


def resample_data(df, expected_rate):
    if df.empty:
        return df  # If DataFrame is empty, return as is

    df = df.sort_values(by="timestamp")  # Ensure timestamps are ordered

    # Build a uniform time grid; include the end if it falls exactly on-grid
    start_t = df["timestamp"].min()
    end_t = df["timestamp"].max()
    step = 1.0 / expected_rate
    time_range = np.arange(start_t, end_t + 0.5 * step, step)

    # Interpolate numeric columns (skip non-numeric)
    resampled = {"timestamp": time_range}
    for col in df.columns:
        if col == "timestamp":
            continue
        if not np.issubdtype(df[col].dtype, np.number):
            # optional: skip non-numeric columns (e.g., categorical flags)
            continue
        interp_func = interp1d(
            df["timestamp"].values,
            df[col].values,
            kind="linear",
            fill_value="extrapolate",
            assume_sorted=True
        )
        resampled[col] = np.round(interp_func(time_range), 2)

    return pd.DataFrame(resampled)

# ---------- IO layout ----------
indir = "../datasets/raw/emotibit/"
outdir = "../datasets/transformed/phys/"

# Pattern: P##_<condition>_<anything>.csv  e.g., P01_HT_Loc2.csv
fname_re = re.compile(r'^(P\d+)_([A-Za-z0-9]+)_.+\.csv$')

file_list = glob(os.path.join(indir, "*.csv"))

for file in file_list:
    print(f"Processing {file}...")

    base = os.path.basename(file)                  # e.g., "P01_HT_Loc2.csv"
    m = fname_re.match(base)
    if not m:
        raise ValueError(
            f"Filename '{base}' does not match pattern 'P<digits>_<condition>_<rest>.csv' "
            "e.g., 'P01_HT_Loc2.csv'. Adjust the regex if your naming differs."
        )

    participant = m.group(1)                       # "P01"
    condition = m.group(2).upper()                 # "HT" normalized
    prefix = f"{participant}_{condition}"          # "P01_HT"

    # Create ONE folder per participant
    participant_dir = os.path.join(outdir, participant)
    os.makedirs(participant_dir, exist_ok=True)

    # Load, expand, resample
    df = pd.read_csv(file)

    eda, ppg, temp, motion = expand_data(df, expected_rates)

    eda_df = pd.DataFrame(eda)
    ppg_df = pd.DataFrame(ppg)
    temp_df = pd.DataFrame(temp)
    motion_df = pd.DataFrame(motion)

    eda_df_resampled   = resample_data(eda_df,   expected_rates["EDA"])
    ppg_df_resampled   = resample_data(ppg_df,   expected_rates["PPG"])
    temp_df_resampled  = resample_data(temp_df,  expected_rates["Temperature"])
    motion_df_resampled= resample_data(motion_df,expected_rates["Motion"])

    # Save flat files inside the participant dir
    eda_df_resampled.to_csv(   os.path.join(participant_dir, f"{prefix}_eda.csv"),    index=False)
    ppg_df_resampled.to_csv(   os.path.join(participant_dir, f"{prefix}_ppg.csv"),    index=False)
    temp_df_resampled.to_csv(  os.path.join(participant_dir, f"{prefix}_temp.csv"),   index=False)
    motion_df_resampled.to_csv(os.path.join(participant_dir, f"{prefix}_motion.csv"), index=False)

    print(f"Saved processed data in {participant_dir}")

print("Processing complete!")
