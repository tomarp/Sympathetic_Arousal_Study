import os
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

# Function to expand JSON data and reconstruct timestamps
def expand_data(df, expected_rates):
    eda_data, ppg_data, temp_data, motion_data = [], [], [], []

    for _, row in df.iterrows():
        timestamp = row["ts"]  # Base timestamp
        
        try:
            sensor_data = json.loads(row["data"])
        except json.JSONDecodeError:
            continue  # Skip rows with corrupted JSON

        # Process EDA Data
        if "eda" in sensor_data:
            interval = 1 / expected_rates["EDA"]
            times = [timestamp + (interval * i) for i in range(len(sensor_data["eda"]))]
            for ts, eda, edl in zip(times, sensor_data["eda"], sensor_data.get("edl", [None] * len(sensor_data["eda"]))):
                eda_data.append({"timestamp": ts, "EDA": round(eda, 2), "EDL": round(edl, 2) if edl is not None else None})

        # Process PPG Data
        if "pgi" in sensor_data:
            interval = 1 / expected_rates["PPG"]
            times = [timestamp + (interval * i) for i in range(len(sensor_data["pgi"]))]
            for ts, pgi, pgr, pgg in zip(times, sensor_data["pgi"], sensor_data.get("pgr", [None] * len(sensor_data["pgi"])), sensor_data.get("pgg", [None] * len(sensor_data["pgi"]))):
                ppg_data.append({"timestamp": ts, "PI": round(pgi, 2), "PR": round(pgr, 2) if pgr is not None else None, "PG": round(pgg, 2) if pgg is not None else None})

        # Process Temperature Data
        if "thr" in sensor_data:
            interval = 1 / expected_rates["Temperature"]
            times = [timestamp + (interval * i) for i in range(len(sensor_data["thr"]))]
            for ts, thr in zip(times, sensor_data["thr"]):
                temp_data.append({"timestamp": ts, "Temp": round(thr, 2)})

        # Process Motion Data
        if "acx" in sensor_data:
            interval = 1 / expected_rates["Motion"]
            times = [timestamp + (interval * i) for i in range(len(sensor_data["acx"]))]
            for ts, acx, acy, acz, gyx, gyy, gyz, mgx, mgy, mgz in zip(
                times, sensor_data["acx"], sensor_data["acy"], sensor_data["acz"], 
                sensor_data["gyx"], sensor_data["gyy"], sensor_data["gyz"], 
                sensor_data["mgx"], sensor_data["mgy"], sensor_data["mgz"]):
                motion_data.append({"timestamp": ts, "ACC_x": round(acx, 2), "ACC_y": round(acy, 2), "ACC_z": round(acz, 2),
                                   "GY_x": round(gyx, 2), "GY_y": round(gyy, 2), "GY_z": round(gyz, 2),
                                   "MG_x": round(mgx, 2), "MG_y": round(mgy, 2), "MG_z": round(mgz, 2)})
    
    return eda_data, ppg_data, temp_data, motion_data

# Function to resample data using linear interpolation
def resample_data(df, expected_rate):
    if df.empty:
        return df  # If DataFrame is empty, return it as is

    df = df.sort_values(by="timestamp")  # Ensure timestamps are ordered
    time_range = np.arange(df["timestamp"].min(), df["timestamp"].max(), 1 / expected_rate)

    # Interpolation for each column except timestamp
    resampled_data = {"timestamp": time_range}
    for col in df.columns:
        if col != "timestamp":
            interp_func = interp1d(df["timestamp"], df[col], kind="linear", fill_value="extrapolate", assume_sorted=True)
            resampled_data[col] = np.round(interp_func(time_range), 2)  # Round off values

    return pd.DataFrame(resampled_data)

# Define the input and output folder paths
indir = "../dataset/emotibit_data/"
outdir = "../outdir/emotibitDataWrangled/"

# Get list of matching CSV files
file_list = glob(os.path.join(indir, "*_emotibit_data.csv"))

for file in file_list:
    print(f"Processing {file}...")
    
    # Extract file name without extension
    file_name = os.path.splitext(os.path.basename(file))[0]
    
    # Create a directory for the file if it doesn't exist
    output_dir = os.path.join(outdir, file_name)
    os.makedirs(output_dir, exist_ok=True)
    
    # Load data
    df = pd.read_csv(file)

    # Expand data
    eda_data, ppg_data, temp_data, motion_data = expand_data(df, expected_rates)

    # Convert expanded data to DataFrames
    eda_df = pd.DataFrame(eda_data)
    ppg_df = pd.DataFrame(ppg_data)
    temp_df = pd.DataFrame(temp_data)
    motion_df = pd.DataFrame(motion_data)

    # Resample using linear interpolation
    eda_df_resampled = resample_data(eda_df, expected_rates["EDA"])
    ppg_df_resampled = resample_data(ppg_df, expected_rates["PPG"])
    temp_df_resampled = resample_data(temp_df, expected_rates["Temperature"])
    motion_df_resampled = resample_data(motion_df, expected_rates["Motion"])

    # Save processed files inside the participant's folder
    eda_df_resampled.to_csv(os.path.join(output_dir, "EDA_data.csv"), index=False)
    ppg_df_resampled.to_csv(os.path.join(output_dir, "PPG_data.csv"), index=False)
    temp_df_resampled.to_csv(os.path.join(output_dir, "Temperature_data.csv"), index=False)
    motion_df_resampled.to_csv(os.path.join(output_dir, "Motion_data.csv"), index=False)

    print(f"Saved processed data in {output_dir}")

print("Processing complete!")
