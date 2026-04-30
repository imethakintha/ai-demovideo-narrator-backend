from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import video, render # අනිත් router files ද මෙලෙසම ඇතුළත් කරන්න

app = FastAPI(title="AI Demo Narrator")

# CORS Settings (Frontend එකට සම්බන්ධ වීමට අනිවාර්යයි)[cite: 1]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(video.router, prefix="/api/video")
# app.include_router(render.router, prefix="/api/render")

@app.get("/")
def root():
    return {"status": "ok", "message": "Backend is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)