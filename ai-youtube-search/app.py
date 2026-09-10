import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Any
import uvicorn

from services.audio_downloader import download_youtube_audio, extract_video_id
from services.gemini_stt import transcribe_with_gemini_35
from services.gemini_chat import answer_question, search_timestamp_by_query

app = FastAPI(title="AI YouTube Search & Assistant")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.path.join(BASE_DIR, "static", "downloads")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(DOWNLOADS_DIR, exist_ok=True)

app.mount("/downloads", StaticFiles(directory=DOWNLOADS_DIR), name="downloads")

class AnalyzeRequest(BaseModel):
    url: str

class ChatRequest(BaseModel):
    transcript: str
    question: str

class SearchRequest(BaseModel):
    query: str
    transcript: str
    segments: Optional[List[Any]] = []

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_file = os.path.join(TEMPLATES_DIR, "index.html")
    if not os.path.exists(index_file):
        raise HTTPException(status_code=404, detail="index.html not found")
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/analyze")
async def analyze_video(req: AnalyzeRequest):
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="유튜브 URL을 입력해 주세요.")

    video_id = extract_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="올바른 유튜브 링크를 인식할 수 없습니다.")

    try:
        # 1. 오디오 다운로드
        download_res = download_youtube_audio(url, DOWNLOADS_DIR)
        audio_path = download_res["audio_path"]

        # 2. Gemini 3.5 Transcribe STT
        stt_res = transcribe_with_gemini_35(audio_path)

        return {
            "success": True,
            "video_id": download_res["video_id"],
            "title": download_res["title"],
            "uploader": download_res["uploader"],
            "thumbnail": download_res["thumbnail"],
            "duration": download_res["duration"],
            "audio_filename": download_res["audio_filename"],
            "transcription": stt_res,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
        }

@app.post("/api/chat")
async def chat_about_video(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="질문 내용을 입력해 주세요.")

    try:
        result = answer_question(req.transcript, req.question)
        return {
            "success": True,
            "data": result,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }

@app.post("/api/search")
async def search_in_video(req: SearchRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="검색어를 입력해 주세요.")

    try:
        result = search_timestamp_by_query(req.query, req.transcript, req.segments or [])
        return {
            "success": True,
            "data": result,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }

if __name__ == "__main__":
    print("[AI YouTube Search Server Started] http://localhost:8001")
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
