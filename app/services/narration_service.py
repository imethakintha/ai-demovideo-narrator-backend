import json
from google import genai
from google.genai import types
from app.core.config import settings

_client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def generate_narration_script(frame_analyses, video_duration, context=""):
    lines = []
    for f in frame_analyses:
        lines.append("[" + str(f["timestamp"]) + "s]: " + f["description"])
    frame_text = "\n".join(lines)

    prompt = (
        "You are an expert technical narrator for software demo videos. "
        "Write a natural voiceover narration script for a developer/IT audience. "
        "Explain WHY behind actions. Be conversational but professional. "
        "Output ONLY valid JSON with NO markdown, NO backticks: "
        '{"title\":\"demo title\",\"segments\":[{"timestamp_start\":0,\"timestamp_end\":5,\"text\":\"narration text\"}],\"total_duration_estimate\":60} '
        "Frame descriptions: " + frame_text + " "
        "Video duration: " + str(video_duration) + "s. "
        "User context: " + (context if context else "none")
    )

    r = _client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[prompt],
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    
    raw = r.text.strip()
    # Markdown backticks තිබුණොත් ඒවා ඉවත් කිරීම
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
            
    return json.loads(raw.strip())