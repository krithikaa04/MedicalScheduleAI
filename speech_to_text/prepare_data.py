import os
import librosa # type: ignore
import numpy as np # type: ignore

# Set the path to the Common Voice dataset
data_dir = "common-voice-data"
# Set the path to save the preprocessed data
save_dir = "preprocessed-data"

# Set the sampling rate (Hz) and duration (seconds) for the audio
sampling_rate = 16000
duration = 10  # seconds



# Loop over each file in the Common Voice dataset
for root, _, files in os.walk(data_dir):
    for filename in files:
        if not filename.endswith(".wav"):  # Process only .wav files
            continue
        filepath = os.path.join(root, filename)
        # Load the audio file
        y, sr = librosa.load(filepath, sr=sampling_rate, duration=duration)
        # Save the preprocessed audio file
        relative_path = os.path.relpath(root, data_dir)
        save_path = os.path.join(save_dir, relative_path, filename[:-4] + ".npy")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        np.save(save_path, y)