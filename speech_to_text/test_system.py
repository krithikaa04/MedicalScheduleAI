import numpy as np
import torch
import logging
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import matplotlib.pyplot as plt
import librosa.display
import sounddevice as sd
import wave
import csv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_npy_audio(audio_path):
    """Load and validate .npy audio file."""
    try:
        audio = np.load(audio_path)
        logging.info(f"Loaded audio shape: {audio.shape}, dtype: {audio.dtype}")
        if audio.ndim > 1:
            audio = audio.mean(axis=1)  # Convert to mono
            logging.info(f"Converted to mono, new shape: {audio.shape}")
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32) / 32768.0 if audio.max() > 1 else audio.astype(np.float32)
            logging.info(f"Normalized audio, min: {audio.min()}, max: {audio.max()}")
        if not np.any(audio):
            logging.warning("Audio is silent or all zeros")
        return audio
    except Exception as e:
        logging.error(f"Failed to load audio: {e}")
        raise

def transcribe_audio(audio, processor, model, sample_rate=16000):
    """Transcribe audio using Wav2Vec 2.0 model."""
    try:
        inputs = processor(audio, sampling_rate=sample_rate, return_tensors="pt", padding=True)
        logging.debug(f"Model input tensor shape: {inputs.input_values.shape}")
        with torch.no_grad():
            logits = model(inputs.input_values).logits
        logging.debug(f"Model logits shape: {logits.shape}")
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)[0]
        logging.info(f"Transcription completed: {transcription}")
        if transcription == "<unk>":
            logging.warning("Transcription returned <unk>. Check audio quality or model configuration.")
        return transcription
    except Exception as e:
        logging.error(f"Transcription failed: {e}")
        raise

def visualize_audio(audio, sample_rate, save_path=None):
    """Visualize the audio waveform."""
    try:
        plt.figure(figsize=(10, 4))
        librosa.display.waveshow(audio, sr=sample_rate)
        plt.title("Audio Waveform")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        if save_path:
            plt.savefig(save_path)
            logging.info(f"Audio waveform saved to {save_path}.")
        else:
            plt.show()
    except Exception as e:
        logging.error(f"Failed to visualize audio: {e}")
        raise

def load_model_and_processor():
    """Load the pretrained Wav2Vec 2.0 model and processor."""
    try:
        processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
        model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
        logging.info("Model and processor loaded successfully.")
        return processor, model
    except Exception as e:
        logging.error(f"Failed to load model and processor: {e}")
        raise

def get_real_transcription(audio_path):
    """Retrieve the real transcription from data.csv based on the audio path."""
    csv_path = "c:/Users/krith/OneDrive/Desktop/PSG/SEM 8/NLP/MedicalScheduleAI/speech_to_text/data.csv"
    try:
        # Extract the audio file name (e.g., audio_58) from the audio_path
        audio_file_name = audio_path.split('/')[-1].replace('.npy', '.wav')

        with open(csv_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if audio_file_name in row["wav"]:
                    logging.info(f"Found matching transcription for {audio_path}.")
                    return row["transcript"]
    except Exception as e:
        logging.error(f"Error reading data.csv: {e}")
    return ""

def test_system(audio_path):
    """Test speech-to-text pipeline."""
    try:
        processor, model = load_model_and_processor()
        audio = load_npy_audio(audio_path)
        if audio is None or len(audio) == 0:
            logging.error("Audio data is empty or invalid.")
            return
        visualize_audio(audio, sample_rate=16000, save_path="figure_1.png")
        transcription = transcribe_audio(audio, processor, model)
        print(f"Raw Transcription: {transcription}")

        # Retrieve real transcription dynamically from data.csv
        real_transcription = get_real_transcription(audio_path)
        print(f"Real Transcription: {real_transcription}")

        return real_transcription
    except Exception as e:
        logging.error(f"Error in test_system: {e}")
        raise

def record_live_audio(duration, sample_rate):
    """Record live audio from the microphone."""
    try:
        logging.info(f"Recording audio for {duration} seconds...")
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()
        return audio_data.flatten()
    except Exception as e:
        logging.error(f"Failed to record live audio: {e}")
        raise

def save_audio_to_wav(audio_data, sample_rate, file_path="temp_audio.wav"):
    """Save audio data to a .wav file."""
    try:
        with wave.open(file_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(sample_rate)
            wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
        logging.info(f"Audio saved to {file_path}")
        return file_path
    except Exception as e:
        logging.error(f"Failed to save audio to .wav: {e}")
        raise

def test_audio_live(duration, sample_rate):
    """Record live audio, transcribe it, and return the transcription."""
    try:
        audio_data = record_live_audio(duration, sample_rate)
        save_audio_to_wav(audio_data, sample_rate)
        processor, model = load_model_and_processor()
        transcription = transcribe_audio(audio_data, processor, model, sample_rate)
        logging.info(f"Live transcription: {transcription}")
        return transcription
    except Exception as e:
        logging.error(f"Error in test_audio_live: {e}")
        return ""

if __name__ == "__main__":
    test_audio_path = "./preprocessed-data/audio_22.npy"  # Adjust if using temp_audio.npy
    test_system(test_audio_path)
    audio = np.load(test_audio_path)
    print(f"Shape: {audio.shape}, Dtype: {audio.dtype}, Min: {audio.min()}, Max: {audio.max()}")