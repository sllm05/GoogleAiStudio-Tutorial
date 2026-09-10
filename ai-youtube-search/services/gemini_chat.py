import os
import re
from google import genai
from google.genai import types

def answer_question(transcript: str, question: str) -> dict:
    """gemini-3.8-flash 모델을 사용하여 영상 트랜스크립트를 기반으로 사용자의 질문에 답합니다."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)

    system_instruction = """
당신은 유튜브 영상의 내용을 분석하여 사용자의 질문에 정확하고 친절하게 답변해주는 AI 어시스턴트입니다.
항상 제공된 [트랜스크립트] 내용을 기반으로 사실에 입각하여 답변하세요.
답변할 때 해당 내용이 언급된 시점의 타임스탬프(예: [01:23] 또는 [00:45])를 반드시 포함해 주세요.
타임스탬프 형식은 반드시 대괄호 안에 [MM:SS] 또는 [HH:MM:SS] 형태로 작성해야 웹에서 클릭 시 영상 재생 위치로 점프할 수 있습니다.
"""

    prompt = f"""
[트랜스크립트]:
{transcript}

[사용자 질문]:
{question}
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=[prompt],
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3,
        ),
    )

    answer_text = response.text or "답변을 생성할 수 없습니다."

    # 답변 내에서 [MM:SS] 타임스탬프 추출
    timestamps = re.findall(r'\[(\d{1,2}:\d{2}(?::\d{2})?)\]', answer_text)

    return {
        "answer": answer_text,
        "timestamps": timestamps,
        "model_used": "gemini-3.8-flash",
    }

def search_timestamp_by_query(query: str, transcript: str, segments: list) -> dict:
    """영상에서 특정 내용(키워드/주제)을 검색하여 가장 적합한 시간대와 위치를 찾습니다."""
    # 1. 1차: 단순 텍스트 키워드 매칭
    keyword_matches = []
    q_lower = query.lower().strip()
    for seg in segments:
        if q_lower in seg.get("text", "").lower():
            keyword_matches.append(seg)

    if keyword_matches:
        best_match = keyword_matches[0]
        return {
            "found": True,
            "target_sec": best_match["start"],
            "timestamp": best_match["timestamp"],
            "matched_text": best_match["text"],
            "matches": keyword_matches[:5],
            "method": "keyword",
        }

    # 2. 2차: Gemini 3.8 Flash 시맨틱 검색 (자연어 질문/의미 매칭)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"found": False, "target_sec": 0, "timestamp": "00:00", "message": "일치하는 내용을 찾을 수 없습니다."}

    client = genai.Client(api_key=api_key)

    prompt = f"""
다음 유튜브 영상의 트랜스크립트에서 사용자가 찾고자 하는 내용("{query}")과 가장 의미상 밀접한 발화 시점의 타임스탬프 [MM:SS]를 하나 찾아주세요.
오직 해당 타임스탬프와 한 줄 요약만 다음 형식으로 출력하세요:
[타임스탬프] 요약 설명

[트랜스크립트]:
{transcript[:8000]}
"""

    try:
        resp = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=[prompt],
            config=types.GenerateContentConfig(temperature=0.1),
        )
        res_text = resp.text or ""
        ts_match = re.search(r'\[(\d{1,2}:\d{2})\]', res_text)

        if ts_match:
            ts_str = ts_match.group(1)
            parts = ts_str.split(":")
            sec = int(parts[0]) * 60 + int(parts[1])
            return {
                "found": True,
                "target_sec": sec,
                "timestamp": ts_str,
                "matched_text": res_text.strip(),
                "method": "semantic_gemini_38",
            }
    except Exception as e:
        print(f"Semantic search error: {e}")

    return {"found": False, "target_sec": 0, "timestamp": "00:00", "message": "일치하는 내용을 찾지 못했습니다."}
