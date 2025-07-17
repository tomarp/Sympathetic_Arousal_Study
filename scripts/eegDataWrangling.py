import os
import pandas as pd

def process_eeg_files(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    for filename in os.listdir(input_directory):
        if filename.endswith(".csv"):
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, filename)
            
            # Load the CSV file
            df = pd.read_csv(input_path)
            
            # Remove columns named 'user' or 'usernames'
            df.drop(columns=[col for col in ['user', 'usernames'] if col in df.columns], errors='ignore', inplace=True)
            
            # Rename 'ts' to 'timestamp' and move it to the first column
            if 'ts' in df.columns:
                df.rename(columns={'ts': 'timestamp'}, inplace=True)
                cols = ['timestamp'] + [col for col in df.columns if col != 'timestamp']
                df = df[cols]
            
            # Save the cleaned file
            df.to_csv(output_path, index=False)
            print(f"Processed and saved: {output_path}")

# Set your input and output directories
indir = "../dataset/eeg_data/"  # Change this to your actual input directory
outdir = "../outdir/eegDataWrangled"  # Change this to your actual output directory

process_eeg_files(indir, outdir)
