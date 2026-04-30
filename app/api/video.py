from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from app.core.config import settings
from app.core.job_manager import create_job, get_job, update_job, JobStatus
from app.services.video_service import get_video_metadata, extract_frames
from app.services.gemini_service import analyze_all_frames
from app.services.narration_service import generate_narration_script
from app.services.tts_service import generate_segments_audio
from app.services.render_service import build_audio_timeline, render_final_video

router = APIRouter()

async def run_pipeline(job_id, video_path, context):
    try:
        update_job(job_id, status=JobStatus.EXTRACTING, progress=10)
        meta = get_video_metadata(video_path)
        frames = await extract_frames(video_path, job_id)

        update_job(job_id, status=JobStatus.ANALYZING, progress=30)
        analyses = await analyze_all_frames(frames)

        update_job(job_id, status=JobStatus.GENERATING, progress=55)
        script = await generate_narration_script(analyses, meta["duration"], context)

        update_job(job_id, status=JobStatus.TTS, progress=70)
        segments = await generate_segments_audio(script["segments"], job_id)

        update_job(job_id, status=JobStatus.RENDERING, progress=85)
        audio = await build_audio_timeline(segments, meta["duration"], job_id)
        output = await render_final_video(video_path, audio, job_id)

        update_job(job_id, status=JobStatus.DONE, progress=100, result=str(output))
    except Exception as e:
        update_job(job_id, status=JobStatus.FAILED, error=str(e))

@router.post("/upload")
async def upload(bg: BackgroundTasks, file: UploadFile = File(...), context: str = ""):
    content = await file.read()
    job = create_job()
    path = settings.UPLOAD_DIR / job.id / file.filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    bg.add_task(run_pipeline, job.id, path, context)
    return {"job_id": job.id}

@router.get("/status/{job_id}")
async def status(job_id: str):
    job = get_job(job_id)
    if not job: raise HTTPException(404)
    return {"status": job.status, "progress": job.progress, "message": job.message}