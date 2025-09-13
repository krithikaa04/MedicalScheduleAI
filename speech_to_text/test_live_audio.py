import pyaudio
import numpy as np
import torch
import logging
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Audio recording parameters
SAMPLING_RATE = 16000  # Wav2Vec 2.0 expects 16kHz
DURATION = 5  # Record for 5 seconds
CHUNK = 1024  # Buffer size
OUTPUT_NPY_PATH = "temp_audio.npy"

def initialize_audio_stream():
    """Initialize the PyAudio stream."""
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLING_RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    return pa, stream

def save_audio(frames):
    """Save recorded audio to a .npy file."""
    audio = np.concatenate(frames).astype(np.float32) / 32768.0
    logging.info(f"Recorded audio shape: {audio.shape}, min: {audio.min()}, max: {audio.max()}")
    if not np.any(audio):
        logging.warning("Audio is silent. Please speak louder or check microphone.")
    np.save(OUTPUT_NPY_PATH, audio)
    logging.info(f"Saved audio to {OUTPUT_NPY_PATH}")
    return OUTPUT_NPY_PATH

def record_audio():
    """Record audio from microphone and save as .npy."""
    try:
        pa, stream = initialize_audio_stream()
        logging.info("Recording for 5 seconds... Speak clearly (e.g., 'Schedule an appointment')")
        frames = [
            np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
            for _ in range(0, int(SAMPLING_RATE / CHUNK * DURATION))
        ]
        logging.info("Recording finished.")
        stream.stop_stream()
        stream.close()
        pa.terminate()
        return save_audio(frames)
    except Exception as e:
        logging.error(f"Recording failed: {e}")
        raise

def load_audio(npy_path):
    """Load audio from a .npy file and ensure it's mono."""
    audio = np.load(npy_path)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
        logging.info(f"Converted audio to mono, shape: {audio.shape}")
    return audio

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
        if transcription.lower() == "<unk>":
            logging.warning("Transcription returned <unk>. Audio may be unclear or too short.")
        return transcription
    except Exception as e:
        logging.error(f"Transcription failed: {e}")
        raise

def load_model_and_processor():
    """Load the pretrained Wav2Vec 2.0 model and processor."""
    try:
        processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
        model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
        logging.info("Loaded pretrained facebook/wav2vec2-base-960h model")
        return processor, model
    except Exception as e:
        logging.error(f"Failed to load model and processor: {e}")
        raise

def main():
    try:
        processor, model = load_model_and_processor() #load model processor
        npy_path = record_audio() #convert live audio to .npy
        audio = load_audio(npy_path)    #preprocess the .npy file
        transcription = transcribe_audio(audio, processor, model)   
        logging.info(f"Starting correction for text: {transcription}")
        print(f"Raw Transcription: {transcription}")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()