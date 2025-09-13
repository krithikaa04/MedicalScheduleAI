import os
from gtts import gTTS # type: ignore

# Directory to save generated training data
output_dir = "training_data"
os.makedirs(output_dir, exist_ok=True)

# Read sentences from the data.txt file
try:
    with open("training_sentences.txt", "r") as file:
        # Skip the first line if it's a title or header
        content = file.readlines()
        if content[0].strip().startswith('"""'):
            sentences = [line.strip() for line in content[1:] if line.strip()]
        else:
            sentences = [line.strip() for line in content if line.strip()]
except FileNotFoundError:
    print("Error: data.txt file not found. Please make sure the file exists in the current directory.")
    exit(1)

# Generate audio files and save transcripts
for i, sentence in enumerate(sentences):
    # Generate audio using gTTS
    tts = gTTS(sentence)
    audio_path = os.path.join(output_dir, f"audio_{i + 1}.wav")
    tts.save(audio_path)

    # Save the corresponding transcript
    transcript_path = os.path.join(output_dir, f"audio_{i + 1}.txt")
    with open(transcript_path, "w") as f:
        f.write(sentence)

print(f"Training data generated in '{output_dir}' directory.")
print(f"Generated {len(sentences)} audio files and transcripts.")