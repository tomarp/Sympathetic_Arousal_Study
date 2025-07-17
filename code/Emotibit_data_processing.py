import pandas as pd
from scipy.signal import butter, filtfilt, savgol_filter, find_peaks
import numpy as np
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.signal import find_peaks, butter, filtfilt, savgol_filter
import os

participant_id = "S01"

# Load and preprocess data
cold_data_path = 'C:/Users/Tomar/dev/WEPOP/WEPOP_summer2024/results/Emotibit_cleaned_annotated/S01A_Cold.csv'
hot_data_path = 'C:/Users/Tomar/dev/WEPOP/WEPOP_summer2024/results/Emotibit_cleaned_annotated/S01B_Hot.csv'

# Read the CSV data
cold_data = pd.read_csv(cold_data_path)
hot_data = pd.read_csv(hot_data_path)

cold_data['DateTime'] = pd.to_datetime(cold_data['DateTime'], errors='coerce')
hot_data['DateTime'] = pd.to_datetime(hot_data['DateTime'], errors='coerce')

out_path = 'C:/Users/Tomar/dev/WEPOP/WEPOP_summer2024/results/analysis_output'
os.makedirs(out_path, exist_ok=True)

# Display the first few rows of both datasets to understand their structure
cold_data.head(), hot_data.head()


## Noise removal

# Define a band-pass filter function for accelerometer and gyroscope data
def bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

# Define a smoothing function using Savitzky-Golay filter for EDA and PPG data
def smooth_signal(data, window_length=51, polyorder=3):
    return savgol_filter(data, window_length, polyorder)

# Apply noise removal for accelerometer (ACC) and gyroscope (GY) data using a band-pass filter
fs = 50  # Assuming a sampling rate of 50 Hz for Emotibit data
lowcut = 0.1  # Low cutoff frequency (Hz)
highcut = 20  # High cutoff frequency (Hz)

# Apply band-pass filter to cold trial data
for axis in ['ACC_x', 'ACC_y', 'ACC_z', 'GY_x', 'GY_y', 'GY_z']:
    cold_data[axis] = bandpass_filter(cold_data[axis], lowcut, highcut, fs)

# Apply band-pass filter to hot trial data
for axis in ['ACC_x', 'ACC_y', 'ACC_z', 'GY_x', 'GY_y', 'GY_z']:
    hot_data[axis] = bandpass_filter(hot_data[axis], lowcut, highcut, fs)

# Apply Savitzky-Golay filter for smoothing EDA and PPG data
for signal in ['EDA', 'PGI', 'PGR', 'PGG']:
    cold_data[signal] = smooth_signal(cold_data[signal])
    hot_data[signal] = smooth_signal(hot_data[signal])

# Display the filtered data to confirm noise removal
cold_data.head(), hot_data.head()


# Calculate total duration of activities where Activity is 'Reading', 'Writing', 'Discussion', or 'Call'
def calculate_activity_duration(data):
    # Filter data for specified activities
    filtered_data = data[data['Activity'].isin(['Reading', 'Writing', 'Discussion', 'Call'])]
    
    # Group by activity and calculate duration
    filtered_data['Duration'] = filtered_data['DateTime'].diff().dt.total_seconds().fillna(0)
    
    # Sum total duration for each activity
    total_duration = filtered_data.groupby('Activity')['Duration'].sum() / 60  # Convert to minutes
    return total_duration

# Calculate durations for both cold and hot datasets
cold_activity_duration = calculate_activity_duration(cold_data).round(2)
hot_activity_duration = calculate_activity_duration(hot_data).round(2)

# Display the results
import ace_tools_open as tools; tools.display_dataframe_to_user(name="Total Duration of Activities (in minutes)", dataframe=pd.DataFrame({'Cold Trial': cold_activity_duration, 'Hot Trial': hot_activity_duration}))


# Feature extraction for physiological signals

# Function to extract EDA features: Peaks, mean, and standard deviation
def extract_eda_features(data):
    eda_peaks, _ = find_peaks(data['EDA'], height=0.05)  # Detect peaks in EDA signal
    eda_mean = np.mean(data['EDA'])
    eda_std = np.std(data['EDA'])
    return len(eda_peaks), eda_mean, eda_std

# Function to calculate heart rate (HR) from PPG signal using peak detection
def extract_ppg_features(data, fs=50):
    peaks_pgi, _ = find_peaks(data['PGI'], distance=fs*0.6)  # Assuming a minimum HR of 60 BPM
    rr_intervals = np.diff(peaks_pgi) / fs  # RR intervals in seconds
    heart_rate = 60 / np.mean(rr_intervals) if len(rr_intervals) > 0 else 0
    hrv = np.std(rr_intervals) if len(rr_intervals) > 1 else 0
    return heart_rate, hrv

# Extract EDA features for both trials
cold_eda_features = extract_eda_features(cold_data)
hot_eda_features = extract_eda_features(hot_data)

# Extract PPG features (HR and HRV) for both trials
cold_ppg_features = extract_ppg_features(cold_data)
hot_ppg_features = extract_ppg_features(hot_data)

# Feature extraction for motion signals

# Function to compute velocity and jerk for accelerometer data
def compute_motion_features(data, fs=50):
    # Calculate velocity by integrating acceleration
    acc_magnitude = np.sqrt(data['ACC_x']**2 + data['ACC_y']**2 + data['ACC_z']**2)
    velocity = np.cumsum(acc_magnitude) / fs

    # Calculate jerk (rate of change of acceleration)
    jerk = np.diff(acc_magnitude) * fs
    
    # Calculate rotational energy using gyroscope data
    gyro_energy = np.sqrt(data['GY_x']**2 + data['GY_y']**2 + data['GY_z']**2)
    
    return np.mean(velocity), np.std(jerk), np.mean(gyro_energy)

# Extract motion features for both trials
cold_motion_features = compute_motion_features(cold_data)
hot_motion_features = compute_motion_features(hot_data)

# Compile extracted features into a dictionary for easy viewing
features_summary = {
    'Cold Trial': {
        'EDA Peaks': cold_eda_features[0],
        'EDA Mean': cold_eda_features[1],
        'EDA Std Dev': cold_eda_features[2],
        'HR': cold_ppg_features[0],
        'HRV': cold_ppg_features[1],
        'Velocity Mean': cold_motion_features[0],
        'Jerk Std Dev': cold_motion_features[1],
        'Gyro Energy Mean': cold_motion_features[2],
    },
    'Hot Trial': {
        'EDA Peaks': hot_eda_features[0],
        'EDA Mean': hot_eda_features[1],
        'EDA Std Dev': hot_eda_features[2],
        'HR': hot_ppg_features[0],
        'HRV': hot_ppg_features[1],
        'Velocity Mean': hot_motion_features[0],
        'Jerk Std Dev': hot_motion_features[1],
        'Gyro Energy Mean': hot_motion_features[2],
    }
}

# Display the extracted features summary
import pandas as pd
import ace_tools_open as tools

features_df = pd.DataFrame(features_summary).T
tools.display_dataframe_to_user(name="Extracted Features Summary", dataframe=features_df)

## Visualization


def filter_activity_data_with_intervals(data):
    """
    Filters activities while maintaining the 'No Activity' periods as 'Perception Survey'.
    Also calculates the duration for each segment.
    """
    data['Activity'] = data['Activity'].replace('No Activity', 'Perception Survey')
    activities = data['Activity'].unique()
    
    activity_intervals = []
    for activity in activities:
        activity_data = data[data['Activity'] == activity]
        start_time = activity_data['DateTime'].min()
        end_time = activity_data['DateTime'].max()
        
        if pd.notnull(start_time) and pd.notnull(end_time):
            duration = (end_time - start_time).seconds // 60  # Convert to minutes
            activity_intervals.append((activity, start_time, end_time, duration))
    
    return data, activity_intervals

def plot_eda_with_annotations(data, participant_id, title, activity_intervals, save_path=None):
    """Plot EDA data with annotations for activities and save the plot."""
    plt.figure(figsize=(15, 7))
    plt.plot(data['DateTime'], data['EDA'], label='EDA', color='#0000FF', alpha=0.8, linewidth=1.5)
    plt.title(f'EDA Levels for {participant_id} during {title}', fontsize=16)
    plt.xlabel('Time')
    plt.ylabel('EDA (µS)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=45)
    
    for activity, start_time, end_time, duration in activity_intervals:
        plt.axvspan(start_time, end_time, facecolor='gray' if activity == 'Perception Survey' else 'green', alpha=0.2)
        if activity != 'Perception Survey':
            mid_time = start_time + (end_time - start_time) / 2
            plt.annotate(f'{activity} ({duration} mins)', xy=(mid_time, data['EDA'].max() * 0.97),
                         fontsize=8, ha='center', color='darkred', fontweight='bold')
    
    plt.tight_layout()
    if save_path:
        eps_path = os.path.join(save_path, f"{participant_id}_{title.replace(' ', '_')}_EDA.eps")
        png_path = os.path.join(save_path, f"{participant_id}_{title.replace(' ', '_')}_EDA.png")
        plt.savefig(eps_path, format='eps')
        plt.savefig(png_path, format='png')
        print(f"Saved EDA plots as: {eps_path} and {png_path}")
    
    plt.show()

def calculate_heart_rate(data, fs=50):
    """Calculate heart rate (HR) and HRV from PPG signal using peak detection."""
    peaks, _ = find_peaks(data['PGI'], distance=fs*0.6)
    rr_intervals = np.diff(peaks) / fs
    heart_rate = 60 / rr_intervals if len(rr_intervals) > 0 else np.array([])
    time_stamps = data['DateTime'].iloc[peaks[1:len(heart_rate)+1]]
    hrv_values = pd.Series(rr_intervals).rolling(window=5).std().dropna()
    hrv_time_stamps = data['DateTime'].iloc[peaks[1:len(hrv_values)+1]]
    return time_stamps, heart_rate, hrv_time_stamps, hrv_values

def annotate_activities(ax, data, y_max):
    """Annotate activities within the plot frame."""
    for activity in ['Reading', 'Writing', 'Discussion', 'Call']:
        activity_data = data[data['Activity'] == activity]
        if not activity_data.empty:
            start_time = activity_data['DateTime'].iloc[0]
            end_time = activity_data['DateTime'].iloc[-1]
            duration = (end_time - start_time).seconds // 60
            mid_time = start_time + (end_time - start_time) / 2
            ax.axvspan(start_time, end_time, facecolor='green', alpha=0.2)
            ax.text(mid_time, y_max, f"{activity} ({duration} mins)", 
                    ha='center', va='top', fontsize=9, color='darkred', fontweight='bold')

def plot_hr_and_hrv_with_annotations(time_stamps, heart_rate, hrv_time_stamps, hrv_values, data, title, save_path=None):
    """Plot HR and HRV trends with activity annotations."""
    plt.figure(figsize=(15, 10))
    
    ax1 = plt.subplot(2, 1, 1)
    ax1.plot(time_stamps, heart_rate, label='Heart Rate (BPM)', color='darkgrey')
    ax1.set_title(f"Heart Rate and HRV Trends for {participant_id} during {title}", fontsize=16)
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Heart Rate (BPM)")
    ax1.grid(True)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=45)
    annotate_activities(ax1, data, max(heart_rate) * 0.99)
    
    ax2 = plt.subplot(2, 1, 2)
    ax2.plot(hrv_time_stamps, hrv_values, label='HRV (SDNN)', color='red')
    ax2.set_xlabel("Time")
    ax2.set_ylabel("HRV (SDNN)")
    ax2.grid(True)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=45)
    annotate_activities(ax2, data, max(hrv_values) * 0.99)
    
    plt.tight_layout()
    if save_path:
        eps_path = os.path.join(save_path, f"{participant_id}_{title.replace(' ', '_')}_HR_HRV.eps")
        png_path = os.path.join(save_path, f"{participant_id}_{title.replace(' ', '_')}_HR_HRV.png")
        plt.savefig(eps_path, format='eps')
        plt.savefig(png_path, format='png')
        print(f"Saved HR and HRV plots for {title}.")
    plt.show()



# Cold Trial Analysis
filtered_cold_data, cold_intervals = filter_activity_data_with_intervals(cold_data)
plot_eda_with_annotations(filtered_cold_data, participant_id, 'Cold Trial', cold_intervals, save_path=out_path)

cold_time_stamps, cold_heart_rate, cold_hrv_time_stamps, cold_hrv_values = calculate_heart_rate(cold_data)
plot_hr_and_hrv_with_annotations(cold_time_stamps, cold_heart_rate, cold_hrv_time_stamps, cold_hrv_values, cold_data, "Cold Trial", save_path=out_path)

# Hot Trial Analysis
filtered_hot_data, hot_intervals = filter_activity_data_with_intervals(hot_data)
plot_eda_with_annotations(filtered_hot_data, participant_id, 'Hot Trial', hot_intervals, save_path=out_path)

hot_time_stamps, hot_heart_rate, hot_hrv_time_stamps, hot_hrv_values = calculate_heart_rate(hot_data)
plot_hr_and_hrv_with_annotations(hot_time_stamps, hot_heart_rate, hot_hrv_time_stamps, hot_hrv_values, hot_data, "Hot Trial", save_path=out_path)

