import os
import re
from google import genai
from google.genai import types

def seconds_to_timestamp(sec: float) -> str:
    """초 단위 시간을 MM:SS 형식 문자열로 변환합니다."""
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m:02d}:{s:02d}"

def timestamp_to_seconds(ts: str) -> float:
    """MM:SS 형식을 초 단위(float)로 변환합니다."""
    parts = ts.strip().split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    return 0.0

def transcribe_with_gemini_35(audio_path: str) -> dict:
    """gemini-3.5-transcribe 모델을 사용하여 오디오 파일에서 타임스탬프와 트랜스크립트를 추출합니다."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)

    # 대용량/장시간 오디오 지원을 위해 Files API에 업로드
    uploaded_file = client.files.upload(file=audio_path)

    config = types.GenerateContentConfig(
        audio_transcription_config=types.AudioTranscriptionConfig(
            word_timestamp=True,
            diarization=True,
        )
    )

    try:
        resp = client.models.generate_content(
            model="gemini-3.5-transcribe",
            contents=[uploaded_file],
            config=config,
        )

        segments = []
        raw_text = ""

        # 응답 파트에서 audio_transcription 추출
        for candidate in resp.candidates:
            if not candidate.content or not candidate.content.parts:
                continue
            for part in candidate.content.parts:
                if hasattr(part, "audio_transcription") and part.audio_transcription:
                    at = part.audio_transcription
                    raw_text = at.text or ""
                    words = at.words or []

                    if words:
                        current_words = []
                        seg_start = 0.0
                        last_end = 0.0

                        for w in words:
                            word_text = getattr(w, "word", "").strip()
                            s_off_str = getattr(w, "start_offset", "0s").rstrip("s")
                            e_off_str = getattr(w, "end_offset", "0s").rstrip("s")

                            try:
                                s_off = float(s_off_str)
                            except ValueError:
                                s_off = last_end
                            try:
                                e_off = float(e_off_str)
                            except ValueError:
                                e_off = s_off + 0.3

                            if not current_words:
                                seg_start = s_off

                            current_words.append(word_text)
                            time_gap = s_off - last_end
                            last_end = e_off

                            # 문장 종결 부호이거나 공백 간격이 크거나 단어가 일정 수 이상이면 세그먼트 생성
                            is_sentence_end = word_text.endswith((".", "?", "!"))
                            is_long = len(current_words) >= 12
                            is_paused = (time_gap > 1.2 and len(current_words) >= 4)

                            if is_sentence_end or is_long or is_paused:
                                seg_text = " ".join(current_words).strip()
                                if seg_text:
                                    segments.append({
                                        "start": round(seg_start, 2),
                                        "end": round(e_off, 2),
                                        "timestamp": seconds_to_timestamp(seg_start),
                                        "text": seg_text,
                                    })
                                current_words = []

                        # 남은 단어 처리
                        if current_words:
                            seg_text = " ".join(current_words).strip()
                            if seg_text:
                                segments.append({
                                    "start": round(seg_start, 2),
                                    "end": round(last_end, 2),
                                    "timestamp": seconds_to_timestamp(seg_start),
                                    "text": seg_text,
                                })

        # 만약 words 파싱이 비어있다면 원시 텍스트 기반 폴백
        if not segments and raw_text:
            lines = raw_text.splitlines()
            est_time = 0.0
            for line in lines:
                line_str = line.strip()
                if line_str:
                    segments.append({
                        "start": round(est_time, 2),
                        "end": round(est_time + 4.0, 2),
                        "timestamp": seconds_to_timestamp(est_time),
                        "text": line_str,
                    })
                    est_time += 4.5

        # 전체 타임라인 텍스트 문자열 생성
        timeline_lines = [f"[{seg['timestamp']}] {seg['text']}" for seg in segments]
        full_transcript = "\n".join(timeline_lines)
        plain_text = " ".join([seg["text"] for seg in segments])

        return {
            "segments": segments,
            "full_transcript": full_transcript,
            "plain_text": plain_text,
            "model_used": "gemini-3.5-transcribe",
        }

    finally:
        try:
            client.files.delete(name=uploaded_file.name)
        except Exception:
            pass
