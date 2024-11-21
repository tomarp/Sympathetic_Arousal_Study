import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import os
import pandas as pd
import ace_tools_open as tools 
from scipy.signal import butter, filtfilt, iirnotch
from scipy.signal import welch


# Load the EEG data files
file_cold = "C:/Users/Tomar/dev/WEPOP/results/EEG_cleaned_annotated/S01A_cold.csv"
file_hot = "C:/Users/Tomar/dev/WEPOP/results/EEG_cleaned_annotated/S01B_hot.csv"

participant_id = 'S01'
out_path = 'C:/Users/Tomar/dev/WEPOP/results/analysis_output/EEG_analysis'

# Read the CSV files
data_cold = pd.read_csv(file_cold)
data_hot = pd.read_csv(file_hot)

# Display the first few rows of the datasets to understand the structure
data_cold.head(), data_hot.head()

# Define bandpass filter parameters
lowcut = 0.5
highcut = 50.0
fs = 256  # Assuming a sampling frequency of 256 Hz

# Define bandpass filter
def bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

# Define notch filter parameters (for 50 Hz interference)
def notch_filter(data, freq=50.0, fs=256, quality=30.0):
    nyquist = 0.5 * fs
    freq = freq / nyquist
    b, a = iirnotch(freq, quality)
    return filtfilt(b, a, data)

# Apply filtering to all EEG channels
def filter_data(df, channels):
    filtered_data = df.copy()
    for ch in channels:
        filtered_data[ch] = notch_filter(bandpass_filter(df[ch], lowcut, highcut, fs))
    return filtered_data

# Channels to filter
channels = ['tp9', 'af7', 'af8', 'tp10']

# Apply filters to both datasets
filtered_cold = filter_data(data_cold, channels)
filtered_hot = filter_data(data_hot, channels)

# Display the first few rows of the filtered data for verification
# filtered_cold.head(), filtered_hot.head()

# Define feature extraction functions
def calculate_time_domain_features(data):
    return {
        'mean': np.mean(data),
        'std_dev': np.std(data),
        'min': np.min(data),
        'max': np.max(data),
        'range': np.max(data) - np.min(data)
    }

def calculate_frequency_domain_features(data, fs=256):
    freqs, psd = np.fft.rfftfreq(len(data), 1/fs), np.abs(np.fft.rfft(data))**2
    return {
        'mean_psd': np.mean(psd),
        'max_psd': np.max(psd),
        'freq_with_max_psd': freqs[np.argmax(psd)]
    }

# Extract features for each channel and activity
def extract_features(df, channels):
    features = {}
    for ch in channels:
        time_features = calculate_time_domain_features(df[ch])
        freq_features = calculate_frequency_domain_features(df[ch])
        features[ch] = {**time_features, **freq_features}
    return features

# Extract features for cold and hot trials
features_cold = extract_features(filtered_cold, channels)
features_hot = extract_features(filtered_hot, channels)

# Convert features to pandas DataFrame for easier saving
features_cold_df = pd.DataFrame(features_cold).T
features_hot_df = pd.DataFrame(features_hot).T

# Save the features to CSV files
cold_output_path = os.path.join(out_path, f"{participant_id}_features_cold.csv")
hot_output_path = os.path.join(out_path, f"{participant_id}_features_hot.csv")

features_cold_df.to_csv(cold_output_path, index=True)
features_hot_df.to_csv(hot_output_path, index=True)

print(f"Features for cold trial saved to {cold_output_path}")
print(f"Features for hot trial saved to {hot_output_path}")

# Display the extracted features
features_cold, features_hot

# Define frequency bands
bands = {
    "Delta": (0.5, 4),
    "Theta": (4, 8),
    "Alpha": (8, 13),
    "Beta": (13, 30),
    "Gamma": (30, 50)
}

# Function to calculate band-specific power
def band_power(data, fs, bands):
    band_powers = {}
    for band, (low, high) in bands.items():
        freqs, psd = welch(data, fs, nperseg=1024)
        band_power = np.trapz(psd[(freqs >= low) & (freqs <= high)], freqs[(freqs >= low) & (freqs <= high)])
        band_powers[band] = band_power
    return band_powers

# Calculate band-specific power for each channel in a dataset
def calculate_band_power(df, channels, fs, bands):
    band_power_data = {}
    for ch in channels:
        band_power_data[ch] = band_power(df[ch], fs, bands)
    return band_power_data

# Calculate band power for both trials
band_power_hot = calculate_band_power(filtered_hot, channels, fs, bands)
band_power_cold = calculate_band_power(filtered_cold, channels, fs, bands)

# Display the results

band_power_hot_df = pd.DataFrame(band_power_hot).T
band_power_cold_df = pd.DataFrame(band_power_cold).T

tools.display_dataframe_to_user(name="Band-Specific Power Consumption (Hot Trial)", dataframe=band_power_hot_df)
tools.display_dataframe_to_user(name="Band-Specific Power Consumption (Cold Trial)", dataframe=band_power_cold_df)

# Save the output to local directory (ensure the directory exists)
def save_band_power_results(band_power_data, trial_type, out_path):
    file_path = os.path.join(out_path, f"{participant_id}_{trial_type}_band_power.csv")
    band_power_data.to_csv(file_path, index=True)
    print(f"Band power results saved to: {file_path}")

save_band_power_results(band_power_hot_df, "hot", out_path)
save_band_power_results(band_power_cold_df, "cold", out_path)

# Bar plot for band-specific power comparison
def band_power_comparison(band_power_hot, band_power_cold, channels, bands, participant_id, save_path=None):
    hot_values = pd.DataFrame(band_power_hot).T
    cold_values = pd.DataFrame(band_power_cold).T
    x = list(bands.keys())

    for channel in channels:
        plt.figure(figsize=(12, 8))
        x_pos = range(len(x))
        width = 0.4
        
        # Plot grid lines behind the bars
        plt.grid(axis='y', linestyle='--', linewidth=0.5, zorder=0)
        
        # Plot bars with zorder > 0
        plt.bar([pos - width/2 for pos in x_pos], hot_values.loc[channel], 
                width=width, label="Hot", color='orange', zorder=3)
        plt.bar([pos + width/2 for pos in x_pos], cold_values.loc[channel], 
                width=width, label="Cold", color='blue', zorder=3)
        
        # Configure plot aesthetics
        plt.xticks(ticks=x_pos, labels=x)
        plt.title(f"Band-Specific Power Comparison for channel {channel} for {participant_id}", fontsize=16)
        plt.ylabel("Power ($\mu V^2/Hz$)", fontsize=14)
        plt.xlabel("Frequency Band", fontsize=14)
        plt.legend()
        plt.tight_layout()

        # Save plots
        if save_path:
            png_path = os.path.join(save_path, f"{participant_id}_psd_barplot_{channel}.png")
            eps_path = os.path.join(save_path, f"{participant_id}_psd_barplot_{channel}.eps")
            plt.savefig(png_path, format='png', bbox_inches='tight')
            plt.savefig(eps_path, format='eps', bbox_inches='tight')
            print(f"Saved bar plot for {channel} as PNG: {png_path}")
            print(f"Saved bar plot for {channel} as EPS: {eps_path}")
        
        # Show plot
        plt.show()

# Execute updated visualizations
band_power_comparison(band_power_hot, band_power_cold, channels, bands, participant_id, save_path=out_path)

# Function to compute band-specific power
def compute_band_power(freq, power, band):
    band_freq = (freq >= band[0]) & (freq <= band[1])
    return np.sum(power[band_freq])

# Analyze and visualize for each activity across all channels
def band_analysis_all_channels(data, channels, fs, title_prefix, participant_id, save_path=None):
    activities = data['Activity'].unique()
    
    for channel in channels:
        band_powers = {band: [] for band in bands.keys()}
        
        for activity in activities:
            activity_data = data[data['Activity'] == activity]
            if not activity_data.empty:
                # Compute PSD for activity
                freq, power = welch(activity_data[channel], fs=fs, nperseg=1024)
                
                # Compute power for each band
                for band_name, band_range in bands.items():
                    band_powers[band_name].append(compute_band_power(freq, power, band_range))
        
        # Plot band powers
        plt.figure(figsize=(12, 8))
        x = np.arange(len(activities))
        width = 0.15
        
        for i, (band_name, powers) in enumerate(band_powers.items()):
            plt.bar(x + i * width, powers, width, label=band_name)
        
        plt.xticks(x + width * 2, activities, rotation=0)
        plt.title(f'Band Power Analysis by Activity - {title_prefix} ({channel}) for {participant_id}', fontsize=16)
        plt.xlabel('Activities', fontsize=14)
        plt.ylabel('Power (µV²)', fontsize=14)
        plt.legend(title="Frequency Bands")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        # Save plots
        if save_path:
            png_path = os.path.join(save_path, f"{participant_id}_{title_prefix}_{channel}_Band_Power.png")
            eps_path = os.path.join(save_path, f"{participant_id}_{title_prefix}_{channel}_Band_Power.eps")
            plt.savefig(png_path, format='png', bbox_inches='tight')
            plt.savefig(eps_path, format='eps', bbox_inches='tight')
            # plt.close()  # Close the plot to avoid display issues
            plt.show()

# Perform band analysis for all channels in Cold and Hot trials
channels = ['tp9', 'af7', 'af8', 'tp10']

band_analysis_all_channels(data_cold, channels, fs, 'Cold', participant_id, save_path=out_path)
band_analysis_all_channels(data_hot, channels, fs, 'Hot', participant_id, save_path=out_path)

def psd_function(filtered_cold, filtered_hot, activities, channels, bands, participant_id, save_path=None):
    band_colors = {
        "Delta": "blue",
        "Theta": "green",
        "Alpha": "yellow",
        "Beta": "orange",
        "Gamma": "red"
    }
    
    for activity in activities:
        cold_data = filtered_cold[filtered_cold['Activity'] == activity]
        hot_data = filtered_hot[filtered_hot['Activity'] == activity]
        
        if not cold_data.empty and not hot_data.empty:
            fig, axs = plt.subplots(2, 2, figsize=(18, 12), sharex=True, sharey=True)
            axs = axs.flatten()
            
            for idx, ch in enumerate(channels):
                ax = axs[idx]
                
                # PSD for cold data
                freqs_cold, psd_cold = welch(cold_data[ch], fs, nperseg=1024)
                ax.semilogy(freqs_cold, psd_cold, label="Cold", linestyle='-')
                
                # PSD for hot data
                freqs_hot, psd_hot = welch(hot_data[ch], fs, nperseg=1024)
                ax.semilogy(freqs_hot, psd_hot, label="Hot")
                
                ax.set_xlim(0, 50)
                ax.set_ylim(1e-2, 1e5)  # Adjust y-axis range
                ax.set_title(f"{ch}")
                ax.grid(True, which="both", linestyle="--", linewidth=0.5)
                
                # Add band annotations
                for band, (low, high) in bands.items():
                    ax.axvspan(low, high, color=band_colors[band], alpha=0.2, label=f"{band} Band")
                
                if idx % 2 == 0:
                    ax.set_ylabel("Power Spectral Density (µV²/Hz)", fontsize=14)
                if idx >= 2:
                    ax.set_xlabel("Frequency (Hz)", fontsize=14)
            
            # Add a single legend for bands
            handles, labels = axs[0].get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            fig.legend(by_label.values(), by_label.keys(), loc='lower center', ncol=7, fontsize='small', bbox_to_anchor=(0.5, 0.9))
            fig.suptitle(f"PSD Comparison for {activity} Activity (Cold vs. Hot Trial) for {participant_id}", y=0.98, fontsize=16)
            plt.tight_layout()
            # fig.tight_layout(rect=[1, 0.0, 1, 0.0])  # Leave space for title and legend

            # Save the figure
            if save_path:
                eps_path = os.path.join(save_path, f"{participant_id}_PSD_{activity}.eps")
                png_path = os.path.join(save_path, f"{participant_id}_PSD_{activity}.png")
                plt.savefig(eps_path, format='eps')
                plt.savefig(png_path, format='png')
                print(f"Saved PSD plot for {activity} as EPS and PNG in {save_path}.")
            
            plt.show()
            plt.close(fig)  # Close the figure to avoid interference with subsequent plots

# Generate updated PSD subplots with shared axes for each activity
psd_function(filtered_cold, filtered_hot, ['Reading', 'Writing', 'Discussion', 'Call'], channels, bands, participant_id, save_path=out_path)

