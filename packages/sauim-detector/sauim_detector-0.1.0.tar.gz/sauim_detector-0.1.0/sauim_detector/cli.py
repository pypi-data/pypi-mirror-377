import argparse
import os
from .loader import load_audio
from .classifier import classify_signal
from joblib import load
import soundfile as sf
import tensorflow_hub as hub
import tensorflow as tf
tf.experimental.numpy.experimental_enable_numpy_behavior()

# Load the pre-trained embedding model
model = hub.load('https://www.kaggle.com/models/google/bird-vocalization-classifier/TensorFlow2/bird-vocalization-classifier/8')

# Load the OCSVM classifier from package data
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "ocsvm_sauim.joblib")
clf = load(MODEL_PATH)

def main():
    """
    Command-line interface for bioacoustic processing and
    Pied tamarin (Saguinus bicolor) vocalization detection.
    - Loads an audio file
    - Runs feature extraction + classification (OCSVM)
    - Saves detection labels in Audacity format
    - Optionally saves filtered audio as .wav
    """
    parser = argparse.ArgumentParser(description="Bioacoustic audio processing and Pied tamarin classification.")
    parser.add_argument("filepath", help="Path to input .wav file")
    parser.add_argument("--save-audio", "-s", action="store_true",
                        help="If set, saves the filtered audio as a .wav file.")
    args = parser.parse_args()

    sr = 32000  # Target sampling rate
    y, sr = load_audio(args.filepath, sr=sr)
    labels = classify_signal(y, sr, model, clf)
    print(f"Total detections: {len(labels)}")

    # Save detection labels to a text file (Audacity label format)
    base, _ = os.path.splitext(args.filepath)
    output_file = base + "_detections.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for start, end, text in labels:
            f.write(f"{start:.2f}\t{end:.2f}\t{text}\n")
    print(f"✅ Labels saved as: {output_file}")

    # Save filtered audio if the flag is set
    if args.save_audio:
        filtered_file = base + "_filtered.wav"
        sf.write(filtered_file, y, sr)
        print(f"✅ Filtered signal saved as: {filtered_file}")
