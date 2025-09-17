# Human Experience in Regulated Offices (HERO) dataset

### Experiment Objective
The primary goal of this experiment was to assess how environmental conditions, particularly temperature, impact the perception of comfort and productivity among office workers. The study focused on how personal characteristics affect multi-domain comfort perception by monitoring physiological responses, complemented by survey-based validation.

### Experimental Setup
A total of 24 participants were involved in the experiment study. Each participant was required to perform a series of four activities in sequence reading, writing, discussion, call in an office setting, with two participants present at a time in the office room. The experiment was conducted in two seperate sessions under different temperature conditions: low (22°C) and high (30°C). The temperature was the only environmental variable altered between two sessions while the activities sequence remained similar. Each session was paired with a different reading content to ensure variation in the cognitive tasks while maintaining the activity occurance.

### Activities
Participants were asked to perform the following four tasks in both the low and high temp conditions:
1. **Reading**: Reading an article on a specific topic.
2. **Writing**: Writing a summary based on the article they had just read.
3. **Discussion**: Engaging in a discussion with a colleague about the same topic.
4. **Conference Call**: Participating in a conference call to further discuss the topic.


### Experimental Design and Data Collection

The sequence of events occurance during each session was as follows:

1. **Perception Survey (Initial)**: Participants first completed a perception survey, which assessed their comfort levels across multiple domains, including:
   - Productivity
   - Thermal comfort
   - Air quality perception
   - Acoustic comfort
   - Visual comfort

2. **Activity 1 (Reading)**: Participants then began the first activity, reading an article.
   
3. **Perception Survey (Post-Reading)**: After reading, they completed the same perception survey to gauge how their comfort perception might have changed.

4. **Activity 2 (Writing Summary)**: Participants proceeded to write a summary of the article they had just read.

5. **Perception Survey (Post-Writing)**: Once again, a perception survey was administered to capture their comfort levels.

6. **Activity 3 (Discussion)**: Participants discussed the article with a colleague.

7. **Perception Survey (Post-Discussion)**: They filled out the perception survey for the third time after the discussion.

8. **Activity 4 (Conference Call)**: Finally, participants engaged in a conference call to discuss the topic further.

9. **Perception Survey (Post-Conference Call)**: After the conference call, the final perception survey was completed.

### Multi-Modal Data Collection

Throughout the experiment, a comprehensive set of data was collected across multiple channels:

- **Video Data**: Webcam recordings of the participants' activities and their conference calls.
- **Survey Data**: Responses from the perception surveys completed before and after each activity.
- **Physiological Data**:
   - **EmotiBit Sensors**: Captured physiological signals such as heart rate, skin temperature, and electrodermal activity.
   - **Muse Headband**: Collected EEG (electroencephalogram) data to monitor brain activity during the tasks.
- **Environmental Data**: Sensors recorded real-time data on temperature, humidity, and other environmental parameters in the room.


### Dataset description

 #### Emotibit
The dataset consists of physiological measurements recorded in cold (22°C) and hot (30°C) temperature over a range of time stamps. Columns in cleaned data include electrodermal activity (EDA, EDL), photoplethysmogram (PGI, PGR, PGG), temperature (Thr), accelerometer (ACC_x, ACC_y, ACC_z), gyroscope (GY_x, GY_y, GY_z), and magnetometer (MG_x, MG_y, MG_z) readings. The Activity column represents the activity being performed.

Columns and Explanation:

DateTime:
A timestamp indicating when the data was recorded.
Example: 2024-08-07 09:37:59.

EDA (Electrodermal Activity):
Measures skin conductance, which is linked to physiological arousal and stress levels.
Example: 0.03.

EDL (Electrodermal Level):
Indicates the baseline level of skin conductance, often used to assess overall skin conductivity over time.
Example: 26516.0.

PGI, PGR, PGG (Photoplethysmography Metrics):
These relate to heart rate and blood volume pulse measurements using .
PGI: PPG Infrared — infrared signal intensity.
PGR: PPG Red — red light signal intensity.
PGG: PPG Green — Green light signal intensity.
Examples: 153681.0, 107456.0, 7227.0.

Thr (Temperature):
Indicates the body or ambient temperature measured by the sensor.
Example: 28.81 (likely in °C).

ACC_x, ACC_y, ACC_z (Accelerometer Data):
Record motion or orientation along the X, Y, and Z axes.
Useful for identifying movement patterns or activity levels.
Examples: 0.05, -0.95, 0.32.

GY_x, GY_y, GY_z (Gyroscope Data):
Measures angular velocity along the X, Y, and Z axes.
Helps assess rotational movements or stability.
Examples: -0.58, 3.45, 0.09.

MG_x, MG_y, MG_z (Magnetometer Data):
Records magnetic field strength in X, Y, and Z directions.
Used for orientation tracking or compass-like functionality.
Examples: -9.0, 14.0, 7.0.

Activity:
Label for the participant's current activity, manually annotated.
Examples: Reading, Writing.

Insights:
The data combines physiological (EDA, PPG) and motion (ACC, GY, MG) signals, allowing for multi-modal analysis. The dataset is well-suited for activity recognition, stress analysis, or motion studies.
Physiological signals (e.g., EDA, PPG) could be analyzed for emotional or stress state detection.
Motion data (accelerometer, gyroscope, magnetometer) might be used to classify activities or detect patterns of movement.

Steps 1: 
   Data Cleaning:
   Handling Missing Values: Check for and interpolate or remove missing data points.
   Noise Removal:
   For accelerometer and gyroscope data: Apply a band-pass filter to remove low-frequency drift and high-frequency noise.
   For EDA and PPG: Use a Savitzky-Golay or Butterworth filter.

Step 2:
   Feature Engineering:
   Extract meaningful features for modeling:

   Physiological Signals:
   EDA: Peaks, mean, and standard deviation.
   PPG (PGI, PGR, PGG): Derive heart rate (HR) and heart rate variability (HRV) using peak detection.
   Motion Signals:
   Accelerometer and Gyroscope: Compute derived metrics like velocity, jerk, or rotational energy.
   Magnetometer: Analyze orientation changes.

Skin Conductance: The typical range for skin conductance is between 0 to 10 microsiemens (μS). Further breakdown:
Baseline: The baseline skin conductance level, or the tonic component, usually ranges from about 0.1 to 5 μS.
Peaks: The phasic component, which includes the skin conductance responses (SCRs) or peaks, can range from 0.1 to several μS above the baseline.

Tonic Component: 
   - Represents the slow-changing baseline skin conductance level (SCL) over time. It reflects general arousal or physiological state.
   - Higher tonic levels indicate sustained arousal, stress, or increased baseline physiological activation.
   - Lower tonic levels suggest relaxation or a lower baseline state of arousal.

Phasic Component: 
   - Represents rapid fluctuations or skin conductance responses (SCRs) triggered by specific stimuli or events. It reflects immediate reactions to stimuli.
   - Higher peaks (SCRs) reflect strong or heightened responses to stimuli.
   - Lower peaks indicate weaker or minimal reactions to events or stimuli.


#### Muse

The EEG data files for participants in cold (trial A) and hot (trial B) conditions. Each dataset contains the following columns:

    DateTime: The timestamp for each EEG reading.
    tp9, af7, af8, tp10: EEG channels with recorded signal values.
    Activity: The activity performed during the recording, which could provide context for event-related changes.

    tp9 and tp10:
    Located near the temporal lobes.
    Important for analyzing brain activity related to auditory processing, memory, and emotional responses.

   af7 and af8:
    Located near the frontal lobe.
    Crucial for studying cognitive processes like attention, problem-solving, and emotional regulation.

EEG frequencies above 50 Hz are typically less useful for analysis as they often consist of noise or muscle artifacts.

# EEG Bands and Their Significance

## Delta (0.5–4 Hz)
- **Associated with**: Deep sleep and restorative processes.  
- **Prominent in**: Infants and during slow-wave sleep.

## Theta (4–8 Hz)
- **Associated to**: Relaxation, meditation, and creativity.  
- **Often seen during**: Light sleep or drowsiness.

## Alpha (8–13 Hz)
- **Associated**: A calm, relaxed, and alert state.  
- **Prominent when**: Eyes are closed and during quiet rest.

## Beta (13–30 Hz)
- **Associated to**: Active thinking, focus, and problem-solving.  
- **Increases during**: Stress or anxiety.

## Gamma (30–100 Hz)
- **Associated with**: High-level cognitive functions like memory, perception, and consciousness.  
- **Indicates**: Neural synchronization across brain regions.

# Frequency Bands in EEG

## 1. Delta Waves
- **Frequency Range:** 0.5 - 4 Hz  
- **Associated States:**  
  - Deep sleep  
  - Unconsciousness  
  - Common in infants  
  Delta waves are the slowest and highest-amplitude brain waves.  
- **Clinical Significance:**  
  Abnormal delta activity can indicate brain injury, infection, or other pathological conditions.  

## 2. Theta Waves
- **Frequency Range:** 4 - 8 Hz  
- **Associated States:**  
  - Drowsiness  
  - Sleep (especially early stages)  
  - Meditation and deep relaxation  
- **Clinical Significance:**  
  Excessive theta activity can be associated with drowsiness, sleep disorders, or certain neurological conditions.  

## 3. Alpha Waves
- **Frequency Range:** 8 - 12 Hz  
- **Associated States:**  
  - Relaxation  
  - Closed eyes  
  - Decreased cortical activity  
  Alpha waves are typically observed in individuals who are relaxed but still somewhat alert.  
- **Clinical Significance:**  
  Alpha waves can serve as markers for relaxation and reduced cortical activity. Abnormal alpha activity may indicate neurological disorders.  

## 4. Beta Waves
- **Frequency Range:** 13 - 30 Hz  
- **Associated States:**  
  - Active thinking  
  - Problem-solving  
  - Motor activity  
  - **Sub-bands:**  
    - **Beta1 (13-15 Hz):** Relaxed yet focused thinking  
    - **Beta2 (15-20 Hz):** Active thinking and problem-solving  
    - **Beta3 (20-30 Hz):** High-level cognitive processing and motor activity  
- **Clinical Significance:**  
  Excessive beta activity can indicate anxiety, stress, or certain neurological conditions.  

## 5. Gamma Waves
- **Frequency Range:** 30 - 100 Hz
- **Associated States:** High-level cognitive processing, attention, and working memory. Gamma waves are involved in the integration of sensory information and are often seen during tasks that require attention.
- **Clinical Significance:** Abnormal gamma activity has been linked to various neurological and psychiatric conditions, including Alzheimer's disease and schizophrenia.

====================================

## Muse Device Overview:

The Muse headband is a consumer-grade EEG (electroencephalogram) device designed primarily for meditation and brainwave monitoring. It detects and records electrical activity in the brain using non-invasive sensors placed on the scalp. 

Electrodes and Sensors: Muse headbands typically use 4-7 sensors to measure brainwave activity. The electrodes are positioned on the forehead and behind the ears to capture EEG signals.
Brainwave Monitoring: It monitors brainwaves, specifically focusing on five types: Delta (sleep), Theta (relaxation/meditation), Alpha (calm/relaxed), Beta (alert/active thinking), and Gamma (concentration).

The EEG channel data provided by the Muse headband — TP9, AF7, AF8, and TP10 — corresponds to specific electrode placements on the scalp, which follow the international 10-20 system for EEG electrode positioning. These channels record electrical activity from different regions of the brain. Here’s what each channel means:

1. **TP9 (Left Temporoparietal Junction)**:
   - Located near the left ear, this channel captures brain activity from the temporoparietal junction, a region involved in sensory integration, perception, and attention.

2. **AF7 (Anterior Frontal Left)**:
   - Positioned on the left side of the forehead, AF7 is near the prefrontal cortex. It measures brain activity related to higher cognitive functions such as attention, decision-making, and working memory.

3. **AF8 (Anterior Frontal Right)**:
   - Placed symmetrically to AF7 but on the right side of the forehead. AF8 also monitors prefrontal cortex activity, which is associated with concentration, reasoning, and emotional regulation.

4. **TP10 (Right Temporoparietal Junction)**:
   - Located near the right ear, this channel records activity from the right temporoparietal junction, which, like TP9, is involved in attention, sensory processing, and integrating information from different sensory modalities.

Together, these channels provide a broad view of brain activity across frontal and temporoparietal regions, offering insights into cognitive processes like attention, focus, and relaxation. In the context of meditation or brain monitoring, the Muse device uses these signals to guide feedback on the user’s mental state, such as calmness or mental engagement.

Columns in the Dataset:
        user: Identifier for the user, in this case, it's always 'S01A'.
        tp9: EEG channel data from the TP9 electrode.
        af7: EEG channel data from the AF7 electrode.
        af8: EEG channel data from the AF8 electrode.
        tp10: EEG channel data from the TP10 electrode.
        ts: Timestamp associated with the EEG recording, represented as a floating-point number.

    Data Types:
        All EEG channel data (tp9, af7, af8, tp10) are of type float64.
        The ts (timestamp) column is also of type float64.
        The user column is of type object.

Initial Observations:

    The EEG data has a high sampling rate given the large number of entries.
    The dataset includes four main EEG channels (TP9, AF7, AF8, TP10) with corresponding timestamp data.
