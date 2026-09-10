import os
import csv
import json
from datetime import datetime
from typing import Optional, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_FILE_PATH = os.path.join(DATA_DIR, "transcripts.csv")

FIELDNAMES = [
    "video_id",
    "url",
    "title",
    "uploader",
    "duration",
    "thumbnail",
    "audio_filename",
    "full_transcript",
    "plain_text",
    "segments_json",
    "created_at",
]

def init_csv_storage():
    """CSV 저장 폴더 및 헤더 파일 초기화"""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, mode="w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

def get_cached_transcript(video_id: str, url: str = "") -> Optional[Dict[str, Any]]:
    """video_id 또는 url로 과거 저장된 트랜스크립트가 있는지 확인하고 반환합니다."""
    init_csv_storage()

    if not os.path.exists(CSV_FILE_PATH):
        return None

    try:
        with open(CSV_FILE_PATH, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # video_id 또는 url 일치 확인
                if (video_id and row.get("video_id") == video_id) or (url and row.get("url") == url):
                    segments = []
                    if row.get("segments_json"):
                        try:
                            segments = json.loads(row["segments_json"])
                        except Exception:
                            segments = []

                    return {
                        "video_id": row.get("video_id"),
                        "url": row.get("url"),
                        "title": row.get("title"),
                        "uploader": row.get("uploader"),
                        "thumbnail": row.get("thumbnail"),
                        "duration": int(row.get("duration") or 0),
                        "audio_filename": row.get("audio_filename"),
                        "transcription": {
                            "segments": segments,
                            "full_transcript": row.get("full_transcript"),
                            "plain_text": row.get("plain_text"),
                            "model_used": "gemini-3.5-transcribe (cached)",
                        },
                        "from_cache": True,
                        "created_at": row.get("created_at"),
                    }
    except Exception as e:
        print(f"CSV read error: {e}")

    return None

def save_transcript_to_csv(data: Dict[str, Any]) -> None:
    """트랜스크립트 및 영상 메타데이터를 CSV 파일에 저장합니다."""
    init_csv_storage()

    video_id = data.get("video_id")
    url = data.get("url")

    # 기존 데이터가 이미 있는지 확인
    existing = get_cached_transcript(video_id, url)
    if existing:
        return

    transcription = data.get("transcription", {})
    segments = transcription.get("segments", [])

    row = {
        "video_id": video_id or "",
        "url": url or "",
        "title": data.get("title") or "",
        "uploader": data.get("uploader") or "",
        "duration": data.get("duration") or 0,
        "thumbnail": data.get("thumbnail") or "",
        "audio_filename": data.get("audio_filename") or "",
        "full_transcript": transcription.get("full_transcript") or "",
        "plain_text": transcription.get("plain_text") or "",
        "segments_json": json.dumps(segments, ensure_ascii=False),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    try:
        with open(CSV_FILE_PATH, mode="a", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow(row)
        print(f"[CSV Saved] video_id: {video_id}, file: {CSV_FILE_PATH}")
    except Exception as e:
        print(f"CSV write error: {e}")
