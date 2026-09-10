# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    # 음성 파일 경로 설정 및 바이너리 읽기
    audio_file_path = "gemini_news.wav"
    if not os.path.exists(audio_file_path):
        audio_file_path = os.path.join(os.path.dirname(__file__), "gemini_news.wav")

    with open(audio_file_path, "rb") as f:
        audio_bytes = f.read()

    model = "gemini-3.5-transcribe"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type="audio/wav",
                ),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        audio_transcription_config=types.AudioTranscriptionConfig(
            word_timestamp=True,
            diarization=True,
        ),
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if text := chunk.text:
            print(text, end="")

if __name__ == "__main__":
    generate()


