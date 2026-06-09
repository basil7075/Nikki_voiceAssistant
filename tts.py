import edge_tts
import io

VOICE = "en-US-AvaNeural"

EMOTION_STYLES = {
"neutral":{"rate":"+0%","pitch":"+0Hz"},
"happy":{"rate":"+10%","pitch":"+5Hz"},
"excited":{"rate":"+15%","pitch":"+10Hz"},
"sad":{"rate": "-10%","pitch": "-5Hz"},
"curious":{"rate": "+5%","pitch": "+5Hz"},
"empathetic": {"rate": "-5%","pitch": "-5Hz"},
"frustrated":{"rate": "+5%","pitch": "-5Hz"}
}

async def synthesize(text,emotion):

    style = EMOTION_STYLES.get(emotion,EMOTION_STYLES["neutral"])

    communicate = edge_tts.Communicate(
        text = text,
        voice = VOICE,
        rate = style["rate"],
        pitch = style["pitch"]
    )

    audio_buffer = io.BytesIO()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.write(chunk["data"])

    return audio_buffer.getvalue()