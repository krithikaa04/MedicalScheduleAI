import os
import numpy as np
import torch
from datasets import Dataset
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, Trainer, TrainingArguments

# Custom data collator for CTC
class CTCDataCollator:
    def __init__(self, processor, padding=True):
        self.processor = processor
        self.padding = padding

    def __call__(self, features):
        # Split features into input_values and labels
        input_features = [{"input_values": feature["input_values"]} for feature in features]
        label_features = [{"input_ids": feature["labels"]} for feature in features]

        # Pad input_values
        batch = self.processor.pad(
            input_features,
            padding=self.padding,
            return_tensors="pt",
        )

        # Pad labels separately
        labels_batch = self.processor.tokenizer.pad(
            label_features,
            padding=self.padding,
            return_tensors="pt",
        )

        # Replace padding with -100 to ignore in CTC loss
        labels = labels_batch["input_ids"].masked_fill(labels_batch["attention_mask"].ne(1), -100)
        batch["labels"] = labels

        return batch

# Step 1: Prepare the dataset
def load_npy_data(data_dir, transcription_file):
    """
    Load .npy audio files and their transcriptions.
    data_dir: Directory containing .npy files
    transcription_file: Text file with format 'filename transcription'
    """
    audio_data = []
    transcriptions = []
    
    with open(transcription_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            fname, transcript = line.strip().split(' ', 1)
            audio_path = os.path.join(data_dir, fname)
            if os.path.exists(audio_path):
                audio = np.load(audio_path)
                audio_data.append(audio)
                transcriptions.append(transcript)
    
    dataset = Dataset.from_dict({"audio": audio_data, "transcription": transcriptions})
    return dataset

# Step 2: Preprocess the data
def preprocess_data(dataset, processor, sample_rate=16000):
    def process_example(example):
        audio = np.array(example["audio"]) if isinstance(example["audio"], list) else example["audio"]
        if audio.ndim > 1:
            audio = audio.mean(axis=0)
        example["input_values"] = processor(audio, sampling_rate=sample_rate, return_tensors="np").input_values[0]
        example["labels"] = processor.tokenizer(example["transcription"]).input_ids
        return example
    
    return dataset.map(process_example, remove_columns=["audio", "transcription"])

# Step 3: Fine-tune the model
def train_model(dataset, output_dir="./wav2vec2-finetuned"):
    # Load pretrained Wav2Vec2 model and processor
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
    
    # Preprocess dataset
    dataset = preprocess_data(dataset, processor)
    
    # Split into train and validation
    dataset = dataset.train_test_split(test_size=0.1)
    
    # Define data collator
    data_collator = CTCDataCollator(processor=processor)

    # Define training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        learning_rate=1e-4,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        save_steps=500,
        eval_steps=500,
        logging_steps=100,
        save_total_limit=2,
    )
    
    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
        processing_class=processor,  # Updated to avoid FutureWarning
        data_collator=data_collator,
    )
    
    # Train the model
    trainer.train()
    
    # Save the model
    model.save_pretrained(output_dir)
    processor.save_pretrained(output_dir)
    print(f"Model saved to {output_dir}")

if __name__ == "__main__":
    data_dir = "./preprocessed-data"
    transcription_file = "./transcriptions.txt"
    dataset = load_npy_data(data_dir, transcription_file)
    train_model(dataset)