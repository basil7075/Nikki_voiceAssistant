import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from assistant import get_response
from tts import synthesize
from stt import transcribe
import base64
import json
import asyncio

app = FastAPI()

app.mount("/static",StaticFiles(directory="static"),name="static")

EXIT_WORDS = ["shut down", "shutdown", "shut down nikki", "shutdown nikki"]

@app.get("/")

async def root():

  return FileResponse("static/index.html")

@app.websocket("/ws")

async def websocket_endpoint(websocket:WebSocket):

  await websocket.accept()

  emotion,text = get_response("greet the user with a short welcome message")
  
  audio_bytes = await synthesize(text,emotion)
  audio_b64 = base64.b64encode(audio_bytes).decode()
  
  await websocket.send_text(json.dumps({
    "type":"response",
    "text":text,
    "emotion":emotion,
    "audio":audio_b64,
    "sender":"nikki"
  }))

  try:

    while True:

      data = await websocket.receive_text()
      message = json.loads(data)
      
      audio_bytes = base64.b64decode(message["data"])

      user_input = transcribe(audio_bytes).lower().strip().rstrip('.')
      print(f"Transcribed: '{user_input}'")


      if not user_input:
          await websocket.send_text(json.dumps({"type": "error", "text": "Couldn't catch that."}))
          continue

      await websocket.send_text(json.dumps({
          "type": "transcript",
          "text": user_input,
          "sender": "user"
      }))

      if user_input in EXIT_WORDS:
        goodbye_audio = await synthesize("Goodbye", "neutral")
        await websocket.send_text(json.dumps({
            "type": "response",
            "text": "Goodbye!",
            "emotion": "neutral",
            "audio": base64.b64encode(goodbye_audio).decode(),
            "sender": "nikki"
        }))
        await asyncio.sleep(3)
        os._exit(0)
      emotion, text = get_response(user_input)
      audio_bytes = await synthesize(text, emotion)
      audio_b64 = base64.b64encode(audio_bytes).decode()

      await websocket.send_text(json.dumps({
          "type": "response",
          "text": text,
          "emotion": emotion,
          "audio": audio_b64,
          "sender": "nikki"
      }))

  except WebSocketDisconnect:
    print("Client Disconnected")