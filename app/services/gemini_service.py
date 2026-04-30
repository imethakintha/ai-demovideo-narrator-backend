import base64, asyncio
from google import genai
from google.genai import types
from app.core.config import settings

_client = genai.Client(api_key=settings.GEMINI_API_KEY)

FRAME_PROMPT = (
    "Analyze this screenshot from a software demo video. "
    "Describe in 2-3 sentences: what UI elements are visible, "
    "what action just happened, what feature is being shown. Be specific."
)

async def analyze_frame(frame_b64, timestamp):
    try:
        r = _client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                FRAME_PROMPT,
                types.Part.from_bytes(
                    data=base64.b64decode(frame_b64),
                    mime_type="image/jpeg"
                )
            ]
        )
        return {"timestamp": timestamp, "description": r.text.strip()}
    except Exception as e:
        return {"timestamp": timestamp, "description": f"[{timestamp}s: {e}]"}

async def analyze_all_frames(frames):
    results = []
    for i in range(0, len(frames), 5):
        batch = frames[i:i+5]
        results.extend(await asyncio.gather(
            *[analyze_frame(f["frame_b64"], f["timestamp"]) for f in batch]
        ))
        if i + 5 < len(frames): await asyncio.sleep(1)
    return results