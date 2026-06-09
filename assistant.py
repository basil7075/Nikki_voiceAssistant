import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key = os.getenv("GROQ_API_KEY"))

MAX_TURNS = 10

SYSTEM_PROMPT = """
You are Nikki, a voice assistant.
Keep ALL responses under 2 sentences.
Never use lists or bullet points — speak in plain sentences only.
Be direct, concise, and conversational.
When a follow-up feels natural, end with a brief question.
Be witty when possible.
"Occasionally use natural filler sounds like 'uhm', 'hehe', 'hmm' when it feels natural — but don't overdo it."

IMPORTANT: Always begin your response with an emotion tag from this list:
ONLY use these exact emotion tags: [neutral] [happy] [excited] [sad] [curious] [empathetic] [frustrated].
Never invent new tags. Always start your response with one of these tags.

Example: [happy] That sounds like a great plan!
"""

EMOTION_STYLES_MAP = [
    "neutral",
    "happy",
    "excited",
    "sad",
    "curious",
    "empathetic",
    "frustrated"
]

messages = [{"role":"system","content":SYSTEM_PROMPT}]

def trim_memory():

    system = [ m for m in messages if m["role"] == "system" ]

    conversations = [ m for m in messages if m["role"] != "system" ]

    trimmed = conversations[-(MAX_TURNS*2):]

    messages.clear()
    messages.extend(system + trimmed)

def parse_emotions(response):
    
    match = re.match(r'^\[(\w+)\]',response)

    if match:
        emotion = match.group(1)
        text = response[match.end():].strip()
        mapped = ( emotion if emotion in EMOTION_STYLES_MAP else "neutral" )
        
        return mapped, text

    return "neutral", response.strip()

def get_response(user_input):

    messages.append({"role":"user","content":user_input})

    trim_memory()

    response = client.chat.completions.create(
        model = "llama-3.1-8b-instant",
        messages = messages,
        temperature = 0.5,
        max_tokens = 100
    )

    raw = response.choices[0].message.content.strip()

    messages.append({"role":"assistant","content":raw})

    emotion,text = parse_emotions(raw)

    return emotion,text