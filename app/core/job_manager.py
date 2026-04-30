import uuid, json
from enum import Enum
from pathlib import Path
from app.core.config import settings

JOBS_FILE = settings.TEMP_DIR / "jobs.json"

class JobStatus(str, Enum):
    PENDING    = "pending"
    EXTRACTING = "extracting_frames"
    ANALYZING  = "analyzing_frames"
    GENERATING = "generating_script"
    TTS        = "generating_voice"
    RENDERING  = "rendering_video"
    DONE       = "done"
    FAILED     = "failed"

def _load():
    if not settings.TEMP_DIR.exists():
        settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
    if JOBS_FILE.exists():
        return json.loads(JOBS_FILE.read_text())
    return {}

def _save(jobs):
    JOBS_FILE.write_text(json.dumps(jobs))

def create_job():
    jobs = _load()
    jid = str(uuid.uuid4())
    jobs[jid] = {"id": jid, "status": "pending", "progress": 0,
                 "message": "Starting...", "result": None, "error": ""}
    _save(jobs)
    # Dictionary එකක් object එකක් විදියට return කිරීම
    class Job: pass
    obj = Job()
    for k, v in jobs[jid].items(): setattr(obj, k, v)
    return obj

def get_job(job_id):
    jobs = _load()
    if job_id not in jobs: return None
    class Job: pass
    obj = Job()
    for k, v in jobs[job_id].items(): setattr(obj, k, v)
    return obj

def update_job(job_id, **kwargs):
    jobs = _load()
    if job_id not in jobs: return None
    jobs[job_id].update(kwargs)
    _save(jobs)
    class Job: pass
    obj = Job()
    for k, v in jobs[job_id].items(): setattr(obj, k, v)
    return obj