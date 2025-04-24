from whisper_live.client import TranscriptionClient

# Connect to the Docker server running on your machine
client = TranscriptionClient(
    "localhost",  # or your server IP if running remotely
    9090,
    lang="en",
    translate=False,
    model="medium.en",
    use_vad=True
)

# Transcribe from microphone (live)
client()
