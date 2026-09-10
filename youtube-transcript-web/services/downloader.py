import os
import re
import yt_dlp
import imageio_ffmpeg

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def get_video_info(url: str) -> dict:
    """유튜브 영상의 기본 정보(제목, 썸네일, 길이, 채널 등)를 다운로드 없이 조회합니다."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title", "Unknown Title"),
            "uploader": info.get("uploader", "Unknown Channel"),
            "duration": info.get("duration", 0),
            "thumbnail": info.get("thumbnail", ""),
            "video_id": info.get("id", ""),
        }

def download_audio(url: str, output_dir: str) -> dict:
    """유튜브 영상에서 오디오를 추출하여 MP3 파일로 저장합니다."""
    os.makedirs(output_dir, exist_ok=True)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    ydl_opts = {
        "format": "bestaudio/best",
        "ffmpeg_location": ffmpeg_exe,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info.get("id", "audio")
        title = info.get("title", "Unknown Title")
        thumbnail = info.get("thumbnail", "")
        duration = info.get("duration", 0)

        audio_filename = f"{video_id}.mp3"
        audio_path = os.path.join(output_dir, audio_filename)

        return {
            "video_id": video_id,
            "title": title,
            "thumbnail": thumbnail,
            "duration": duration,
            "audio_filename": audio_filename,
            "audio_path": audio_path,
        }
