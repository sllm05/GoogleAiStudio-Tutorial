import os
from google import genai
from google.genai import types

def transcribe_audio(audio_path: str, model_name: str = "gemini-3.6-flash") -> dict:
    """Gemini API를 사용하여 오디오 파일에서 트랜스크립트와 타임스탬프를 추출합니다."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경 변수가 설정되어 있지 않습니다.")

    client = genai.Client(api_key=api_key)

    # 대용량/장시간 오디오 지원을 위해 Files API에 업로드
    uploaded_file = client.files.upload(file=audio_path)

    prompt = """
다음 오디오의 음성을 듣고 한국어(또는 원어)로 정확하게 전사해 주세요.
결과는 아래 세 가지 형식으로 구분하여 작성해 주세요:

### [1. 타임스탬프 트랜스크립트]
발화 구간의 타임스탬프([분:초 - 분:초])와 함께 대사를 정확히 기록하세요.

### [2. 전체 줄글 텍스트]
타임스탬프 없이 자연스럽게 읽을 수 있는 전체 텍스트입니다.

### [3. 핵심 내용 요약]
전체 대화/영상의 핵심 내용을 3~5줄로 간결하게 요약해 주세요.
"""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[uploaded_file, prompt],
        )
        full_text = response.text or ""

        # 섹션별 파싱
        transcript_ts = ""
        plain_text = ""
        summary = ""

        if "### [1. 타임스탬프 트랜스크립트]" in full_text:
            parts = full_text.split("### [1. 타임스탬프 트랜스크립트]")
            after_ts = parts[1]
            if "### [2. 전체 줄글 텍스트]" in after_ts:
                ts_part, after_plain = after_ts.split("### [2. 전체 줄글 텍스트]")
                transcript_ts = ts_part.strip()
                if "### [3. 핵심 내용 요약]" in after_plain:
                    p_part, s_part = after_plain.split("### [3. 핵심 내용 요약]")
                    plain_text = p_part.strip()
                    summary = s_part.strip()
                else:
                    plain_text = after_plain.strip()
            else:
                transcript_ts = after_ts.strip()
        else:
            transcript_ts = full_text
            plain_text = full_text

        return {
            "raw_response": full_text,
            "timestamp_transcript": transcript_ts,
            "plain_text": plain_text,
            "summary": summary,
            "model_used": model_name,
        }
    finally:
        # 업로드된 임시 원격 파일 정리
        try:
            client.files.delete(name=uploaded_file.name)
        except Exception:
            pass
