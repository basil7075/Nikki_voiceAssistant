# Nikki - Voice Assistant

A conversational voice assistant with an interactive web UI built with FastAPI, Groq, and Edge TTS.

## Features
- Push-to-talk voice input
- Natural language responses via Groq LLM (LLaMA 3.1)
- Speech synthesis via Edge TTS
- Emotion-aware responses
- Live conversation transcript
- Animated orb UI

## Tech Stack
- **Backend:** FastAPI, Python
- **STT:** Groq Whisper
- **LLM:** Groq (LLaMA 3.1 8B Instant)
- **TTS:** Edge TTS
- **Frontend:** HTML, CSS, JavaScript (WebSocket)

## Setup

1. Clone the repo
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file:
   ```
   GROQ_API_KEY=your_api_key_here
   ```
4. Run:
   ```
   uvicorn main:app --reload
   ```
5. Open `http://localhost:8000`

## Usage
- Hold the mic button to speak
- Release to send
- Say **"shut down"** to exit
```
