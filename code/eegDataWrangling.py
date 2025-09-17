import os
import re
import pandas as pd

def process_eeg_files(input_directory, output_root):
    # Regex: P##_<condition>_<rest>.csv  → groups: (participant, condition)
    # Examples matched: P01_HT_Session1.csv, P12_Base_runA.csv
    fname_re = re.compile(r'^(P\d+)_([A-Za-z0-9]+)_.+\.csv$')

    for filename in os.listdir(input_directory):
        if not filename.lower().endswith(".csv"):
            continue

        m = fname_re.match(filename)
        if not m:
            # Fail fast to avoid writing into wrong places
            raise ValueError(
                f"Filename '{filename}' does not match pattern "
                "'P<digits>_<condition>_<rest>.csv' (e.g., 'P01_HT_Session1.csv')."
            )

        participant = m.group(1)               # e.g., P01
        condition = m.group(2).upper()         # normalize e.g., HT
        prefix = f"{participant}_{condition}"  # e.g., P01_HT

        input_path = os.path.join(input_directory, filename)

        # Create one folder per participant
        participant_dir = os.path.join(output_root, participant)
        os.makedirs(participant_dir, exist_ok=True)

        # Define output filename (flat per participant)
        output_filename = f"{prefix}_eeg.csv"
        output_path = os.path.join(participant_dir, output_filename)

        # Load the CSV
        df = pd.read_csv(input_path)

        # Drop user/usernames if present
        cols_to_drop = [col for col in ['user', 'usernames'] if col in df.columns]
        if cols_to_drop:
            df.drop(columns=cols_to_drop, inplace=True, errors='ignore')

        # Rename 'ts' → 'timestamp' and move to first column
        if 'ts' in df.columns:
            df = df.rename(columns={'ts': 'timestamp'})
        # If 'timestamp' exists (original or renamed), move it to the front
        if 'timestamp' in df.columns:
            other_cols = [c for c in df.columns if c != 'timestamp']
            df = df[['timestamp'] + other_cols]

        # Save cleaned file into participant folder
        df.to_csv(output_path, index=False)
        print(f"Processed and saved: {output_path}")

# Set your input and output directories
indir = "../datasets/raw/eeg/"
outdir = "../datasets/transformed/phys/"

process_eeg_files(indir, outdir)
