from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from app.core.job_manager import get_job, JobStatus

router = APIRouter()

@router.get("/download/{job_id}")
async def download_result(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job.status != JobStatus.DONE:
        raise HTTPException(400, f"Job not complete yet: {job.status}")
    if not job.result:
        raise HTTPException(404, "Output file not found")

    output_path = Path(job.result)
    if not output_path.exists():
        raise HTTPException(404, f"Output file missing: {output_path}")

    return FileResponse(
        path=str(output_path),
        media_type="video/mp4",
        filename=f"narrated_demo_{job_id[:8]}.mp4",
        headers={"Content-Disposition": f"attachment; filename=narrated_demo_{job_id[:8]}.mp4"}
    )

@router.get("/health")
def health():
    return {"status": "ok"}