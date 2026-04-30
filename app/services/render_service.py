import asyncio
from pathlib import Path
from app.core.config import settings

async def build_audio_timeline(segments, video_duration, job_id):
    out = settings.TEMP_DIR / job_id / "merged_audio.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    
    # Timestamps අනුව පිළිවෙලට සකස් කිරීම
    segments = sorted(segments, key=lambda s: s["timestamp_start"])
    parts, cursor = [], 0.0
    
    for seg in segments:
        gap = seg["timestamp_start"] - cursor
        if gap > 0.05:
            parts.append({"type": "silence", "duration": gap})
        dur = seg.get("audio_duration", 3.0)
        parts.append({"type": "audio", "path": seg["audio_path"], "duration": dur})
        cursor = seg["timestamp_start"] + dur
        
    tail = video_duration - cursor
    if tail > 0.05:
        parts.append({"type": "silence", "duration": tail})

    # FFmpeg commands සකස් කිරීම
    inputs, fparts, labels, li, ii = [], [], [], 0, 0
    for p in parts:
        if p["type"] == "silence":
            lbl = f"[s{li}]"
            fparts.append(f"aevalsrc=0:d={p['duration']:.3f}{lbl}")
            labels.append(lbl)
            li += 1
        else:
            inputs.extend(["-i", p["path"]])
            labels.append(f"[{ii}]")
            ii += 1

    n = len(labels)
    fc = (";".join(fparts) + (";" if fparts else "")) + "".join(labels) + f"concat=n={n}:v=0:a=1[out]"
    
    cmd = ["ffmpeg", *inputs, "-filter_complex", fc,
           "-map", "[out]", "-t", str(video_duration),
           "-ar", "44100", "-ac", "1", str(out), "-y"]
           
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    _, err = await proc.communicate()
    
    if proc.returncode != 0:
        raise RuntimeError(f"Audio merge failed: {err.decode()}")
    return out

async def render_final_video(video_path, audio_path, job_id, output_filename="narrated_demo.mp4"):
    op = settings.OUTPUT_DIR / job_id / output_filename
    op.parent.mkdir(parents=True, exist_ok=True)
    
    # වීඩියෝ සහ ඕඩියෝ එකතු කිරීමේ FFmpeg command එක[cite: 1]
    cmd = ["ffmpeg", "-i", str(video_path), "-i", str(audio_path),
           "-map", "0:v:0", "-map", "1:a:0",
           "-c:v", "libx264", "-preset", "fast", "-crf", "23",
           "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", "-shortest", str(op), "-y"]
           
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    _, err = await proc.communicate()
    
    if proc.returncode != 0:
        raise RuntimeError(f"Render failed: {err.decode()}")
    return op