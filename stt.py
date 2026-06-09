import os
import io
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def transcribe(audio_bytes):

  audio_file = io.BytesIO(audio_bytes)
  audio_file.name = "audio.webm"
  
  transcription = client.audio.transcriptions.create(
    model = "whisper-large-v3-turbo",
    file = audio_file,
    response_format = "text",
    language = "en"
  )

  return transcription.strip() if transcription else ""