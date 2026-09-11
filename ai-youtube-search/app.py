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
from services.csv_storage import get_cached_transcript, save_transcript_to_csv

app = FastAPI(title="AI YouTube Search & Assistant")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DOWNLOADS_DIR = os.path.join(STATIC_DIR, "downloads")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
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

    # 1. 과거 저장된 CSV 캐시 확인
    cached_data = get_cached_transcript(video_id=video_id, url=url)
    if cached_data:
        print(f"[Cache Hit] CSV에 저장된 트랜스크립트를 불러옵니다: {video_id}")
        return {
            "success": True,
            **cached_data
        }

    try:
        # 2. 캐시가 없는 경우: 신규 오디오 다운로드
        print(f"[New Video] 신규 음원 다운로드 및 전사 시작: {video_id}")
        download_res = download_youtube_audio(url, DOWNLOADS_DIR)
        audio_path = download_res["audio_path"]

        # 3. Gemini 3.5 Transcribe STT
        stt_res = transcribe_with_gemini_35(audio_path)

        result_data = {
            "success": True,
            "video_id": download_res["video_id"],
            "url": url,
            "title": download_res["title"],
            "uploader": download_res["uploader"],
            "thumbnail": download_res["thumbnail"],
            "duration": download_res["duration"],
            "audio_filename": download_res["audio_filename"],
            "transcription": stt_res,
            "from_cache": False,
        }

        # 4. CSV 파일에 저장
        save_transcript_to_csv(result_data)

        return result_data
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
