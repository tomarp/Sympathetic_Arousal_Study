import pandas as pd
import pytz

# Load the survey responses dataset again
file_path = 'C:/Users/Tomar/dev/datasets/WEPOP_summer2024/survey_responses.csv'
survey_data = pd.read_csv(file_path)

# Filter and process relevant columns for the analysis
perception_columns = [
    'user_id',
    'session_start',
    'thermal_perception_Q1: What is your thermal sensation in this room? [-2,2]',
    'thermal_perception_Q2: Choose your thermal comfort in this room [-2,2]',
    'thermal_perception_Q3: How would you describe thermal environment in this room? [-2,2]',
    'visual_perception_Q1: What is your visual sensation right now? [-2,2]',
    'visual_perception_Q2: Choose your visual comfort in this room [-2,2]',
    'visual_perception_Q3: How would you rate the glare level from artificial lighting sources in this environment? [-2,2]',
    'productivity_perception_Q1: How would you judge your productivity at this stage? [-2,2]',
    'productivity_perception_Q2: How does the thermal condition in this office environment affect your productivity at this stage? [-2,2]',
    'productivity_perception_Q3: How does the lighting in this office environment affect your productivity at this stage? [-2,2]',
    'productivity_perception_Q4: How does the Acoustic condition in this office environment affect your productivity at this stage? [-2,2]',
    'productivity_perception_Q5: How does the air Quality in this office environment affect your productivity at this stage? [-2,2]',
    'acoustic_perception_Q1: What is your acoustic sensation in this environment? [-2,2]',
    'acoustic_perception_Q2: Choose your acoustic comfort in this room? [-2,2]',
    'acoustic_perception_Q3: How would you rate the overall noise level in this environment? [-2,2]',
    'air_quality_perception_Q1: What is your air quality sensation in this room? [-2,2]',
    'air_quality_perception_Q2: Choose your air quality comfort in this room? [-2,2]',
    'air_quality_perception_Q3: How would you rate the air quality in this environment? [-2,2]',
]

# Subset the data to the relevant columns for perception analysis
perception_data = survey_data[perception_columns]

# Convert perception columns (excluding user_id and session_start) to integers
perception_only_columns = perception_columns[2:]  # Exclude 'user_id' and 'session_start'
perception_data[perception_only_columns] = perception_data[perception_only_columns].apply(pd.to_numeric, errors='coerce').astype('Int64')

# Convert session_start to datetime for ordering survey rounds
perception_data['session_start'] = pd.to_datetime(perception_data['session_start'], utc=True)

# Convert the time to CET (Central European Time) with +2:00 during summer (CEST)
cet = pytz.timezone('Europe/Berlin')
perception_data['session_start'] = perception_data['session_start'].dt.tz_convert(cet)

# Remove the timezone offset and microseconds, keeping only date and time up to seconds
perception_data['session_start'] = perception_data['session_start'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Grouping data by 'user_id' to ensure each user has all five perception rounds
grouped_perception_data = perception_data.groupby('user_id').apply(
    lambda x: x.sort_values(by='session_start')).reset_index(drop=True)

# Update labels to match the instruction of skipping the Initial Survey
labels = ['perception_survey_1', 'perception_survey_2', 'perception_survey_3', 'perception_survey_4', 'perception_survey_5']

# Assign perception survey labels skipping 'Initial Survey' based on the order of appearance for each user
grouped_perception_data['Label'] = grouped_perception_data.groupby('user_id').cumcount().map(dict(enumerate(labels, 1)))

# Filter out the "Initial Survey" from the data
filtered_perception_data = grouped_perception_data.dropna(subset=['Label'])

# Save the resulting DataFrame to a CSV file in the local directory
output_file_path = 'C:/Users/Tomar/dev/WEPOP_summer2024/results/perception_survey_responses.csv'
filtered_perception_data.to_csv(output_file_path, index=False)

# Output file path for the user
print(f"File saved successfully at: {output_file_path}")
