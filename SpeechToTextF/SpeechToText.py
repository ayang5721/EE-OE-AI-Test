# === OVERVIEW ===
# This Cloud Function will run 100% in the cloud.
# When an audio file is uploaded to a Google Cloud Storage bucket,
# it will automatically:
# 1. Trigger a transcription job using Speech-to-Text V2 (batch mode, unlogged)
# 2. Save the resulting transcript as a .txt file to an output bucket.

# === REQUIREMENTS ===
# - Enable Cloud Functions, Cloud Storage, and Speech-to-Text V2
# - Deploy this Cloud Function with a trigger on the "input" bucket
# - Set environment variables for project_id, output_bucket

import os
from google.cloud import speech_v2
from google.cloud import storage
from google.cloud.speech_v2 import RecognitionConfig
import subprocess
import json

def get_audio_duration(gcs_uri):
    # Use ffprobe via subprocess to get duration (requires ffprobe available in the Cloud Function environment)
    try:
        command = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            gcs_uri
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        info = json.loads(result.stdout)
        duration = float(info['format']['duration'])
        if duration < 14400:
            return 14400  # default to 4 hours if duration is less than 4 hours
        return duration
    except Exception as e:
        print(f"Could not determine duration: {e}")
        return 14400  # default to 4 hours if duration can't be determined

def transcribe_audio(event, context):
    # === Environment Configs ===
    project_id = os.environ["PROJECT_ID"]
    output_bucket_name = os.environ["OUTPUT_BUCKET"]
    input_bucket_name = event["bucket"]
    audio_filename = event["name"]
    gcs_uri = f"gs://{input_bucket_name}/{audio_filename}"

    print(f"Received file: {gcs_uri}")

    speech_client = speech_v2.SpeechClient()
    storage_client = storage.Client()

    # === Config for transcription ===
    config = RecognitionConfig(
        auto_decoding_config={},
        language_codes=["en-US"],
        model="latest_long",
        features={"enable_unlogged_recognition": True},
    )

    request = speech_v2.BatchRecognizeRequest(
        recognizer=f"projects/{project_id}/locations/global/recognizers/_",
        config=config,
        files=[{"uri": gcs_uri}],
    )

    operation = speech_client.batch_recognize(request=request)
    print("Transcription started. Calculating timeout based on audio duration...")

    # === Dynamically determine timeout based on duration ===
    duration = get_audio_duration(gcs_uri)  # in seconds
    timeout_seconds = int(duration * 2)  # 2x buffer

    response = operation.result(timeout=timeout_seconds)
    transcript_lines = []
    for result in response.results:
        for alt in result.alternatives:
            transcript_lines.append(alt.transcript)

    transcript_text = "\n".join(transcript_lines)
    output_filename = os.path.splitext(audio_filename)[0] + ".txt"

    # === Write transcript to output bucket ===
    output_bucket = storage_client.bucket(output_bucket_name)
    blob = output_bucket.blob(output_filename)
    blob.upload_from_string(transcript_text, content_type="text/plain")

    print(f"Transcription complete. Saved to: gs://{output_bucket_name}/{output_filename}")