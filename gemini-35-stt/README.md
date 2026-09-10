# Gemini 3.5 STT(Transcribe) 코드 라인별(Line-by-Line) 상세 해설

본 문서는 Google AI Studio에서 제공하는 최신 전사 모델인 `gemini-3.5-transcribe`를 사용하여 오디오 파일(`gemini_news.wav`)을 음성 인식(STT)하고 타임스탬프 및 화자 분리(Diarization) 기능과 함께 텍스트로 스트리밍 변환하는 `gemini-35-stt-example.py`의 전체 코드를 한 줄씩 분석한 설명서입니다.

---

## 1. 사전 요구사항 및 라이브러리 임포트 (Line 1 ~ 8)

```python
1: # To run this code you need to install the following dependencies:
2: # pip install google-genai
3: 
4: import base64
5: import os
6: from google import genai
7: from google.genai import types
8: 
```

* **Line 1~2:** 주석. 최신 Google GenAI SDK 설치 명령어입니다. (`pip install google-genai`)
* **Line 4:** `import base64` - 오디오 등 바이너리 인코딩/디코딩에 활용되는 표준 라이브러리입니다.
* **Line 5:** `import os` - 오디오 파일 경로 확인(`os.path`) 및 API 키 환경 변수(`GEMINI_API_KEY`)를 읽기 위한 모듈입니다.
* **Line 6:** `from google import genai` - Gemini 2.x/3.x 모델들과 통신하기 위한 구글 공식 GenAI 클라이언트 라이브러리입니다.
* **Line 7:** `from google.genai import types` - Content, Part, AudioTranscriptionConfig 등 타입 힌트와 설정 객체들을 제공하는 모듈입니다.

---

## 2. API 클라이언트 초기화 및 오디오 파일 로드 (Line 10 ~ 22)

```python
10: def generate():
11:     client = genai.Client(
12:         api_key=os.environ.get("GEMINI_API_KEY"),
13:     )
14: 
15:     # 음성 파일 경로 설정 및 바이너리 읽기
16:     audio_file_path = "gemini_news.wav"
17:     if not os.path.exists(audio_file_path):
18:         audio_file_path = os.path.join(os.path.dirname(__file__), "gemini_news.wav")
19: 
20:     with open(audio_file_path, "rb") as f:
21:         audio_bytes = f.read()
22: 
```

* **Line 10:** `def generate():` - STT 전사 작업을 실행하는 메인 함수 정의입니다.
* **Line 11~13:** `client = genai.Client(...)` - 시스템 환경 변수 `GEMINI_API_KEY`에서 키 값을 읽어 GenAI 클라이언트를 생성합니다.
* **Line 16:** `audio_file_path = "gemini_news.wav"` - 인식 대상이 될 기본 오디오 파일명을 지정합니다.
* **Line 17~18:** `if not os.path.exists(...)` - 현재 실행 위치(CWD)에 파일이 없을 경우, 본 파이썬 스크립트가 위치한 폴더 기준의 경로로 안전하게 폴백(Fallback)하도록 처리합니다.
* **Line 20~21:** `with open(audio_file_path, "rb") as f:` / `audio_bytes = f.read()` - 파일을 바이너리 읽기(`"rb"`) 모드로 열어 파일 전체 바이트를 메모리에 로드합니다.

---

## 3. 모델 지정 및 인라인 오디오 콘텐츠 구성 (Line 23 ~ 34)

```python
23:     model = "gemini-3.5-transcribe"
24:     contents = [
25:         types.Content(
26:             role="user",
27:             parts=[
28:                 types.Part.from_bytes(
29:                     data=audio_bytes,
30:                     mime_type="audio/wav",
31:                 ),
32:             ],
33:         ),
34:     ]
```

* **Line 23:** `model = "gemini-3.5-transcribe"` - 구글 AI 스튜디오의 전용 음성 인식(STT) 최신 모델명을 지정합니다.
* **Line 24~26:** `contents = [types.Content(role="user", parts=[...])]` - 모델에 전달할 사용자 요청 콘텐츠 리스트를 생성합니다.
* **Line 28~31:** `types.Part.from_bytes(...)` - **핵심 파트**. 20MB 이하의 오디오 파일은 별도 서버 업로드 과정 없이 `from_bytes`를 통해 직접 인라인 바이트(`audio/wav`)로 즉시 API에 전송할 수 있습니다.

---

## 4. 고급 전사 옵션 설정 (Line 35 ~ 40)

```python
35:     generate_content_config = types.GenerateContentConfig(
36:         audio_transcription_config=types.AudioTranscriptionConfig(
37:             word_timestamp=True,
38:             diarization=True,
39:         ),
40:     )
```

* **Line 35:** `generate_content_config = types.GenerateContentConfig(...)` - 모델 호출 구성을 담는 설정 객체입니다.
* **Line 36:** `audio_transcription_config=types.AudioTranscriptionConfig(...)` - 음성 전사 전용 옵션을 활성화합니다.
* **Line 37:** `word_timestamp=True` - 단어 단위의 정확한 시작/종료 시점(타임스탬프) 정보를 함께 추출하도록 지정합니다.
* **Line 38:** `diarization=True` - 화자 분리(화자가 2명 이상일 때 화자별로 발화를 구분하는 기능)를 활성화합니다.

---

## 5. 스트리밍 전사 결과 출력 및 실행 진입점 (Line 42 ~ 52)

```python
42:     for chunk in client.models.generate_content_stream(
43:         model=model,
44:         contents=contents,
45:         config=generate_content_config,
46:     ):
47:         if text := chunk.text:
48:             print(text, end="")
49: 
50: if __name__ == "__main__":
51:     generate()
```

* **Line 42~46:** `client.models.generate_content_stream(...)` - 모델이 음성을 인식하면서 실시간으로 텍스트 토큰을 스트리밍 방식으로 반환합니다.
* **Line 47~48:** `if text := chunk.text:` / `print(text, end="")` - 도착한 텍스트 조각을 줄바꿈 없이 실시간으로 터미널 콘솔에 출력합니다.
* **Line 50~51:** 파이썬 파일이 직접 실행되면 `generate()`를 호출하여 전사를 시작합니다.
