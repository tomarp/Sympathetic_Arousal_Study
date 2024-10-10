# WEPOP summer 2024 documentation

## EmotiBit Device Overview

EmotiBit is a wearable sensor platform designed for real-time physiological data collection. It typically attaches to the back of an existing wearable device, such as a smartwatch, and measures a range of biometric signals including:

    - Electrodermal Activity (EDA): Measures skin conductance, which is associated with sweat gland activity and can indicate psychological or physiological arousal.
    - Electrocardiogram (ECG): Measures electrical activity of the heart.
    - Photoplethysmography (PPG): Measures blood volume changes, commonly used for heart rate monitoring.
    - Temperature: Measures skin temperature.
    - Accelerometer and Gyroscope: Measures motion and orientation.
    - Inertial Measurement Unit (IMU): Combines accelerometer and gyroscope data to capture movement in 3D space.

    
The data column contains the following physiological and device signals:

    acx, acy, acz: Accelerometer data along x, y, and z axes.
    bat: Battery level of the device.
    eda: Electrodermal Activity data.
    edl: Probably Electrodermal Level or some related measure.
    gyx, gyy, gyz: Gyroscope data along x, y, and z axes.
    mgx, mgy, mgz: Magnetometer data along x, y, and z axes.
    pgg, pgi, pgr: Possibly related to photoplethysmography (PPG) or other physiological signals.
    thr: Could be related to a threshold or temperature measurement.
    device_address and user_id: Metadata related to the device and user.


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