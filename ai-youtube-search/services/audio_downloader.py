import os
import re
import yt_dlp
import imageio_ffmpeg

def extract_video_id(url: str) -> str:
    """유튜브 URL에서 비디오 ID를 추출합니다."""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:shorts\/)([0-9A-Za-z_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""

def download_youtube_audio(url: str, output_dir: str) -> dict:
    """유튜브 영상에서 고음질 오디오(MP3)를 추출하고 메타데이터를 반환합니다."""
    os.makedirs(output_dir, exist_ok=True)
    video_id = extract_video_id(url)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    outtmpl = os.path.join(output_dir, "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "ffmpeg_location": ffmpeg_exe,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        actual_id = info.get("id") or video_id or "youtube_audio"
        title = info.get("title", "유튜브 영상")
        uploader = info.get("uploader", "알 수 없음")
        thumbnail = info.get("thumbnail", f"https://img.youtube.com/vi/{actual_id}/hqdefault.jpg")
        duration = info.get("duration", 0)

        audio_filename = f"{actual_id}.mp3"
        audio_path = os.path.join(output_dir, audio_filename)

        return {
            "video_id": actual_id,
            "title": title,
            "uploader": uploader,
            "thumbnail": thumbnail,
            "duration": duration,
            "audio_filename": audio_filename,
            "audio_path": audio_path,
        }
