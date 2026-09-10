import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from services.downloader import download_audio, get_video_info
from services.transcriber import transcribe_audio

app = FastAPI(title="YouTube Audio & Transcript Web Service")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.path.join(BASE_DIR, "static", "downloads")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# 다운로드된 오디오 정적 서빙
app.mount("/downloads", StaticFiles(directory=DOWNLOADS_DIR), name="downloads")

class ProcessRequest(BaseModel):
    url: str
    model: str = "gemini-3.6-flash"

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_file = os.path.join(TEMPLATES_DIR, "index.html")
    if not os.path.exists(index_file):
        raise HTTPException(status_code=404, detail="Template not found")
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/process")
async def process_youtube(req: ProcessRequest):
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="유튜브 URL을 입력해 주세요.")

    try:
        # 1. 유튜브 오디오 다운로드
        download_res = download_audio(url, DOWNLOADS_DIR)
        audio_path = download_res["audio_path"]
        audio_filename = download_res["audio_filename"]

        # 2. Gemini STT 트랜스크립트 추출
        transcription_res = transcribe_audio(audio_path, model_name=req.model)

        return {
            "success": True,
            "video_info": {
                "video_id": download_res.get("video_id"),
                "title": download_res.get("title"),
                "thumbnail": download_res.get("thumbnail"),
                "duration": download_res.get("duration"),
            },
            "audio_filename": audio_filename,
            "transcription": transcription_res,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    print("[Server Started] http://localhost:8000")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
