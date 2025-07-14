# === OVERVIEW ===
# This local Python script mimics the cloud-based transcription system.
# It:
# 1. Monitors a local "input" folder for audio files
# 2. Transcribes each file using the free version of Google's SpeechRecognition API
# 3. Saves each transcript to a local "output" folder as a .txt file

# === REQUIREMENTS ===
# - pip install SpeechRecognition pydub
# - Use only short files (<60s) to stay within free Google Web API limits

import os
import speech_recognition as sr
from pydub.utils import mediainfo

# === FOLDERS ===
INPUT_FOLDER = "local_input_audio"
OUTPUT_FOLDER = "local_transcripts"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Get Audio Duration (to scale timeout logic for consistency) ===
def get_audio_duration(file_path):
    try:
        info = mediainfo(file_path)
        return float(info['duration'])  # in seconds
    except Exception as e:
        print(f"Error getting duration for {file_path}: {e}")
        return 60  # default to 60s

# === Main Function ===
def transcribe_audio_local():
    recognizer = sr.Recognizer()

    for audio_file in os.listdir(INPUT_FOLDER):
        if not audio_file.lower().endswith((".wav", ".mp3", ".flac")):
            continue

        input_path = os.path.join(INPUT_FOLDER, audio_file)
        output_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(audio_file)[0] + ".txt")
        print(f"Transcribing: {input_path}")

        try:
            # Load audio file
            with sr.AudioFile(input_path) as source:
                audio_data = recognizer.record(source)

            # Transcribe using free Google Web API
            transcript = recognizer.recognize_google(audio_data)

            # Save to .txt file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(transcript)

            print(f"Saved transcript: {output_path}")

        except sr.UnknownValueError:
            print(f"Could not understand: {audio_file}")
        except sr.RequestError as e:
            print(f"API error for {audio_file}: {e}")

if __name__ == "__main__":
    transcribe_audio_local()