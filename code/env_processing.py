#!/usr/bin/env python3
"""
Usage:
    python env_processing.py --input ./data/input --output ./data/output
    %run env_processing.py --input ../datasets/raw/env --output ../datasets/transformed/env/

"""

import pandas as pd
import glob
import os
import argparse


def find_csv_files(directory, pattern):
    return glob.glob(os.path.join(directory, pattern))


def check_data_quality(df, cols):
    issues = []
    for col in cols:
        if col not in df.columns:
            continue
        n_missing = int(df[col].isnull().sum())
        n_unique = int(df[col].nunique(dropna=True))
        if n_missing > 0 or n_unique <= 1:
            issues.append((col, n_missing, n_unique))
    return issues


def convert_time_to_utc(df, time_col='Time'):
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    df[time_col] = df[time_col].dt.tz_localize('Europe/Berlin', ambiguous='NaT', nonexistent='NaT')
    df[time_col] = df[time_col].dt.tz_convert('UTC')
    df[time_col] = df[time_col].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    df.rename(columns={time_col: 'datetime'}, inplace=True)
    return df


def process_session_files(input_dir, output_dir, label, pattern, keep_columns):
    files = find_csv_files(input_dir, pattern)
    if not files:
        print(f"No files found for pattern '{pattern}' in {input_dir}.")
        return

    dfs = []
    print(f"\nProcessing session '{label}': {len(files)} file(s) found.")
    for fpath in files:
        print(f"  Reading file: {os.path.basename(fpath)}")
        df = pd.read_csv(fpath)

        available_cols = [col for col in keep_columns if col in df.columns]
        missing_cols = [col for col in keep_columns if col not in df.columns]
        if missing_cols:
            print(f"    Warning: missing columns: {missing_cols}")
        df = df[available_cols].copy()

        if 'Time' in df.columns:
            df = convert_time_to_utc(df)
            df = df[['datetime'] + [col for col in df.columns if col != 'datetime']]

        issues = check_data_quality(df, df.columns)
        if issues:
            print("    Data quality issues:")
            for col, n_missing, n_unique in issues:
                print(f"      - {col}: missing={n_missing}, unique={n_unique}")

        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"env_{label}.csv")
    combined.to_csv(output_file, index=False)
    print(f"✅ Saved combined data for '{label}' to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Convert CEST to UTC and merge environmental sensor CSV files.")
    parser.add_argument("--input", required=True, help="Path to input directory with CSV files.")
    parser.add_argument("--output", required=True, help="Path to output directory to save merged CSV files.")
    args = parser.parse_args()

    input_dir = args.input
    output_dir = args.output

    keep_columns = [
        'Time',
        'AirTemperature',
        'Relative Humidity',
        'Air velocity',
        'Luxmetro_1',
        'Net_Rad_1',
        'RTD/Tpav',
        'RTD/T60cm',
        'RTD/T110cm',
        'RTD/T130cm',
        'RTD/T10cm',
        'RTD/Tglobe'
    ]

    sessions = {
        'HT': 'HT*.csv',
        'LT': 'LT*.csv'
    }

    for label, pattern in sessions.items():
        process_session_files(input_dir, output_dir, label, pattern, keep_columns)


if __name__ == "__main__":
    main()
