import subprocess, asyncio, json, base64
from pathlib import Path
from app.core.config import settings

def get_video_metadata(video_path):
    r = subprocess.run(
        ["ffprobe","-v","quiet","-print_format","json",
         "-show_streams","-show_format", str(video_path)],
        capture_output=True, text=True)
    data = json.loads(r.stdout)
    vs = next((s for s in data["streams"] if s["codec_type"]=="video"), None)
    duration = float(data["format"].get("duration", 0))
    return {"duration": duration,
            "width":   int(vs.get("width",0)) if vs else 0,
            "height":  int(vs.get("height",0)) if vs else 0}

async def extract_frames(video_path, job_id):
    fd = settings.TEMP_DIR / job_id / "frames"
    fd.mkdir(parents=True, exist_ok=True)
    sr = settings.FRAME_SAMPLE_RATE
    cmd = ["ffmpeg","-i",str(video_path),
           "-vf", f"fps=1/{sr}","-q:v","2","-vframes","300",
           str(fd / "frame_%04d.jpg"),"-y"]
    p = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await p.communicate()
    frames = []
    for i, fp in enumerate(sorted(fd.glob("frame_*.jpg"))):
        b64 = base64.b64encode(fp.read_bytes()).decode()
        frames.append({"timestamp": i * sr, "frame_b64": b64})
    return frames