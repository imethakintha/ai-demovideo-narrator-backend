import asyncio, numpy as np, soundfile as sf
from pathlib import Path
from app.core.config import settings

_pipeline = None

def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        from kokoro import KPipeline
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _pipeline = KPipeline(lang_code=settings.TTS_LANGUAGE, device=device)
    return _pipeline

async def text_to_speech(text, output_path):
    loop = asyncio.get_event_loop()
    def _gen():
        p = _get_pipeline()
        chunks = [a for _, _, a in p(text, voice=settings.TTS_VOICE, speed=settings.TTS_SPEED)]
        sf.write(str(output_path), np.concatenate(chunks), 24000)
        return output_path
    return await loop.run_in_executor(None, _gen)

async def generate_segments_audio(segments, job_id):
    d = settings.TEMP_DIR / job_id / "audio_segments"
    d.mkdir(parents=True, exist_ok=True)
    result = []
    for i, seg in enumerate(segments):
        p = d / f"segment_{i:03d}.wav"
        await text_to_speech(seg["text"], p)
        result.append({**seg, "audio_path": str(p), "audio_duration": sf.info(str(p)).duration})
    return result