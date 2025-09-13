import streamlit as st
import speech_recognition as sr
import tempfile
import os
import sounddevice as sd
import numpy as np
import wave

def recognize_speech():
    """
    Function to use the microphone to record audio and convert it to text.
    
    Returns:
        str: The transcribed text from speech, or empty string if failed
    """
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # For Streamlit web app, we need to simulate recording since we can't
        # directly access the user's microphone. In a real app, we'd use
        # WebRTC or similar technology.
        # This is a workaround for demonstration purposes:
        
        st.info("This is a simulation of voice recording (in a real app, you would speak into your microphone).")
        
        # 1. Create a temporary file to simulate audio recording
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            temp_filename = tmp_file.name
        
        # 2. For demonstration, we'll use a predefined sample text
        sample_texts = [
            "I need to take Lisinopril 10mg once daily in the morning for my blood pressure.",
            "Take Metformin 500mg twice a day with meals for 3 months.",
            "I'm supposed to take one Aspirin 81mg every morning after breakfast.",
            "My doctor prescribed Simvastatin 20mg at bedtime daily.",
            "I need to take Levothyroxine 50mcg every morning on an empty stomach."
        ]
        
        # Let the user select a sample text for demonstration
        selected_sample = st.selectbox(
            "For demonstration, select one of these sample medication instructions:",
            sample_texts
        )
        
        # 3. Simulate processing time
        with st.spinner("Processing audio..."):
            # Wait a moment to simulate processing
            import time
            time.sleep(2)
        
        # 4. Return the selected sample text as if it was transcribed
        return selected_sample
        
    except Exception as e:
        st.error(f"Error during speech recognition: {str(e)}")
        return ""

def record_real_audio():
    """
    This function would be used in a real implementation to record actual audio.
    Not used in this demo, but included for reference.
    
    Returns:
        str: The transcribed text from speech
    """
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Record audio from microphone
        with sr.Microphone() as source:
            st.write("Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            st.write("Listening... Speak now.")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
        
        # Recognize speech using Google Speech Recognition
        text = recognizer.recognize_google(audio)
        print(text)
        return text
    
    except sr.WaitTimeoutError:
        st.error("No speech detected within the timeout period.")
        return ""
    except sr.UnknownValueError:
        st.error("Could not understand audio. Please try again.")
        return ""
    except sr.RequestError as e:
        st.error(f"Could not request results; {str(e)}")
        return ""
    except Exception as e:
        st.error(f"Error during speech recognition: {str(e)}")
        return ""

def record_real_audio_to_file(file_path="temp_audio.wav", duration=5, sample_rate=16000):
    """
    Record real-time audio from the microphone and save it to a file.

    Args:
        file_path (str): Path to save the recorded audio file.
        duration (int): Duration of the recording in seconds.
        sample_rate (int): Sampling rate for the audio.

    Returns:
        str: Path to the saved audio file.
    """
    try:
        print(f"Recording audio for {duration} seconds...")
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()  # Wait until the recording is finished

        # Save the audio as a .wav file
        with wave.open(file_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(sample_rate)
            wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())

        print(f"Audio recorded and saved to {file_path}")
        return file_path
    except Exception as e:
        print(f"Error recording audio: {e}")
        return None

if __name__ == "__main__":
    st.title("Speech Recognition Helper Test")

    option = st.radio("Choose a mode to test:", ("Simulated Speech Recognition", "Real Audio Recording"))

    if option == "Simulated Speech Recognition":
        st.write("Testing simulated speech recognition...")
        result = recognize_speech()
        st.write(f"Recognized Text: {result}")
    elif option == "Real Audio Recording":
        st.write("Testing real audio recording...")
        result = record_real_audio()
        st.write(f"Recognized Text: {result}")
