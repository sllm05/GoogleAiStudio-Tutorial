# Gemini 3.1 Flash TTS 코드 라인별(Line-by-Line) 상세 해설

본 문서는 Google AI Studio에서 제공하는 최신 음성 생성 모델인 `gemini-3.1-flash-tts-preview`를 사용하여 텍스트 및 오디오 프로필을 기반으로 고품질 음성(WAV)을 생성하는 `gemini-31-tts-example.py`의 전체 코드를 한 줄씩 분석한 설명서입니다.

---

## 1. 사전 요구사항 및 라이브러리 임포트 (Line 1 ~ 10)

```python
1: # To run this code you need to install the following dependencies:
2: # pip install google-genai
3: 
4: import mimetypes
5: import os
6: import re
7: import struct
8: from google import genai
9: from google.genai import types
10: 
```

* **Line 1~2:** 주석. Google GenAI 최신 SDK인 `google-genai` 패키지 설치 가이드입니다. (`pip install google-genai`)
* **Line 4:** `import mimetypes` - 파일 확장자 및 MIME 타입을 다루기 위한 표준 모듈입니다.
* **Line 5:** `import os` - 시스템 환경 변수(`GEMINI_API_KEY`)를 읽어오기 위한 표준 라이브러리입니다.
* **Line 6:** `import re` - 정규표현식 모듈(MIME 파싱 등 부가 작업용 표준 라이브러리)입니다.
* **Line 7:** `import struct` - 바이너리 데이터를 특정 포맷(바이트 구조체)으로 패킹/언패킹하는 모듈로, WAV 오디오 헤더(RIFF/WAVE 포맷 규격)를 직접 조립할 때 사용됩니다.
* **Line 8:** `from google import genai` - 구글의 공식 차세대 GenAI 클라이언트 패키지입니다.
* **Line 9:** `from google.genai import types` - API 호출 시 필요한 파라미터(Content, Config, SpeechConfig 등)의 데이터 타입을 정의한 모듈입니다.

---

## 2. 바이너리 파일 저장 함수 (Line 12 ~ 16)

```python
12: def save_binary_file(file_name, data):
13:     f = open(file_name, "wb")
14:     f.write(data)
15:     f.close()
16:     print(f"File saved to to: {file_name}")
```

* **Line 12:** `def save_binary_file(file_name, data):` - 생성된 오디오 바이너리 데이터를 디스크 파일로 저장하는 유틸리티 함수 정의입니다.
* **Line 13:** `f = open(file_name, "wb")` - 바이너리 쓰기(`"wb"`) 모드로 파일을 엽니다.
* **Line 14:** `f.write(data)` - 순수 바이트(WAV 파일 데이터)를 파일에 기록합니다.
* **Line 15:** `f.close()` - 열려 있던 파일 핸들을 안전하게 닫습니다.
* **Line 16:** `print(f"File saved to to: {file_name}")` - 저장이 완료된 파일 경로를 콘솔에 출력합니다.

---

## 3. 클라이언트 생성 및 프롬프트 구성 (Line 19 ~ 44)

```python
19: def generate():
20:     client = genai.Client(
21:         api_key=os.environ.get("GEMINI_API_KEY"),
22:     )
23: 
24:     model = "gemini-3.1-flash-tts-preview"
25:     contents = [
26:         types.Content(
27:             role="user",
28:             parts=[
29:                 types.Part.from_text(text="""Read the following transcript based on the audio profile.
30: 
31: # Audio Profile
32: warm
33: 
34: ## Scene:
35: A modern, high-tech TV newsroom studio with crisp broadcast acoustics and subtle ambient room tone.
36: 
37: ## Sample Context:
38: A lively news anchor is urgently delivering breaking tech news with great excitement and disbelief at the price drop.
39: 
40: ## Transcript:
41: [excited] 속보입니다! 구글이 차세대 플래그십 AI, '제미나이 4.0 프로'를 깜짝 출시했습니다! [gasps] 그런데 성능보다 더 놀라운 건 바로 가격인데요. 기존 모델의 10분의 1도 안 되는 파격적인 가격으로 책정되었습니다! [laughs] 업계에서는 \"이 가격이면 거의 무료 배포 아니냐\"며 발칵 뒤집혔습니다. [enthusiastic] 지금 바로 AI 스튜디오에서 만나보실 수 있습니다!"""),
42:             ],
43:         ),
44:     ]
```

* **Line 19:** `def generate():` - TTS 음성 생성 전체 과정을 수행하는 메인 로직 함수입니다.
* **Line 20~22:** `client = genai.Client(...)` - 환경 변수에 설정된 `GEMINI_API_KEY`를 가져와 Gemini API 클라이언트를 초기화합니다.
* **Line 24:** `model = "gemini-3.1-flash-tts-preview"` - 사용할 모델을 지정합니다. 구글 AI 스튜디오의 최신 플래시 TTS 프리뷰 모델입니다.
* **Line 25~28:** `contents = [types.Content(role="user", parts=[...])]` - 사용자가 전달할 프롬프트 메시지 구조를 정의합니다.
* **Line 29:** `types.Part.from_text(...)` - 텍스트 형태의 지시문과 대사를 파트로 생성합니다.
* **Line 31~32:** `# Audio Profile \n warm` - 목소리의 전체적인 음색 프로필(따뜻한 톤)을 지정합니다.
* **Line 34~35:** `## Scene:` - 음향 공간감(현대적인 방송 스튜디오의 음향 울림, 잔향 등)을 설정합니다.
* **Line 37~38:** `## Sample Context:` - 화자의 감정 및 연기 상황(뉴스 앵커가 놀라움과 흥분 속에 긴급 속보를 전달하는 상황)을 지정합니다.
* **Line 40~41:** `## Transcript:` - 실제 읽을 대사 본문입니다. `[excited]`, `[gasps]`, `[laughs]`와 같은 감정/호흡 태그를 포함하여 AI가 생동감 넘치게 연기하도록 유도합니다.

---

## 4. 음성 생성 설정 및 보이스 지정 (Line 45 ~ 57)

```python
45:     generate_content_config = types.GenerateContentConfig(
46:         temperature=1,
47:         response_modalities=[
48:             "audio",
49:         ],
50:         speech_config=types.SpeechConfig(
51:             voice_config=types.VoiceConfig(
52:                 prebuilt_voice_config=types.PrebuiltVoiceConfig(
53:                     voice_name="Kore"
54:                 )
55:             )
56:         ),
57:     )
```

* **Line 45:** `generate_content_config = types.GenerateContentConfig(...)` - 모델 생성 파라미터를 묶는 설정 객체입니다.
* **Line 46:** `temperature=1` - 생성의 다양성과 표현력 수준을 지정합니다.
* **Line 47~49:** `response_modalities=["audio"]` - **핵심 파라미터**. 텍스트가 아닌 **오디오 모달리티**로 결과를 반환받도록 지정합니다.
* **Line 50~56:** `speech_config=...` - 사전 제공 음성(Prebuilt Voice) 중 `"Kore"`라는 이름의 목소리를 선택합니다.

---

## 5. 스트리밍 수신 및 단일 버퍼 누적 (Line 59 ~ 77)

```python
59:     audio_data_buffer = bytearray()
60:     mime_type = "audio/L16;rate=24000"
61: 
62:     print("오디오 생성 중...")
63:     for chunk in client.models.generate_content_stream(
64:         model=model,
65:         contents=contents,
66:         config=generate_content_config,
67:     ):
68:         if chunk.parts is None:
69:             continue
70:         if chunk.parts[0].inline_data and chunk.parts[0].inline_data.data:
71:             inline_data = chunk.parts[0].inline_data
72:             mime_type = inline_data.mime_type
73:             audio_data_buffer.extend(inline_data.data)
74:         else:
75:             if text := chunk.text:
76:                 print(text)
77: 
```

* **Line 59:** `audio_data_buffer = bytearray()` - 쪼개져서 전송되는 오디오 조각(PCM 바이트)들을 하나의 온전한 데이터로 모으기 위한 바이트 배열 버퍼입니다.
* **Line 60:** `mime_type = "audio/L16;rate=24000"` - 기본 오디오 포맷(Linear 16-bit PCM, 24kHz)을 초기값으로 지정합니다.
* **Line 62:** 콘솔에 생성 시작 메시지를 출력합니다.
* **Line 63~67:** `client.models.generate_content_stream(...)` - 모델로부터 실시간으로 데이터 조각(chunk)을 스트리밍 방식으로 수신합니다.
* **Line 68~69:** 청크에 파트 데이터가 없으면 다음 루프로 넘어갑니다.
* **Line 70:** 청크의 첫 번째 파트에 바이너리 데이터(`inline_data`)가 포함되어 있는지 검사합니다.
* **Line 71~72:** 실제 전달된 오디오의 `mime_type`을 갱신합니다.
* **Line 73:** `audio_data_buffer.extend(inline_data.data)` - **중요**: 각 조각을 개별 파일로 만들지 않고 전체 버퍼에 순차적으로 바이트를 누적합니다.
* **Line 74~76:** 만약 오디오 대신 텍스트 응답이 함께 온 경우 텍스트를 출력합니다.

---

## 6. 단일 WAV 파일 변환 및 저장 (Line 78 ~ 82)

```python
78:     if audio_data_buffer:
79:         output_filename = "gemini_news.wav"
80:         complete_wav = convert_to_wav(bytes(audio_data_buffer), mime_type)
81:         save_binary_file(output_filename, complete_wav)
82:         print(f"생성 완료: {output_filename}")
```

* **Line 78:** 수신된 오디오 바이트 데이터가 있는지 확인합니다.
* **Line 79:** 최종 저장될 파일명을 `"gemini_news.wav"`로 정의합니다.
* **Line 80:** `complete_wav = convert_to_wav(...)` - 모아둔 전체 PCM 바이트에 정식 WAV 헤더(44바이트)를 결합하여 완전한 WAV 파일 바이너리로 만듭니다.
* **Line 81:** `save_binary_file(...)` - 완성된 단일 오디오 파일을 디스크에 저장합니다.
* **Line 82:** 완료 메시지를 출력합니다.

---

## 7. WAV 포맷 헤더 생성 유틸리티 (Line 85 ~ 123)

```python
85: def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
...
93:     parameters = parse_audio_mime_type(mime_type)
94:     bits_per_sample = parameters["bits_per_sample"]
95:     sample_rate = parameters["rate"]
96:     num_channels = 1
97:     data_size = len(audio_data)
98:     bytes_per_sample = bits_per_sample // 8
99:     block_align = num_channels * bytes_per_sample
100:    byte_rate = sample_rate * block_align
101:    chunk_size = 36 + data_size
...
105:    header = struct.pack(
106:        "<4sI4s4sIHHIIHH4sI",
107:        b"RIFF",          # ChunkID
108:        chunk_size,       # ChunkSize
109:        b"WAVE",          # Format
110:        b"fmt ",          # Subchunk1ID
111:        16,               # Subchunk1Size
112:        1,                # AudioFormat (PCM)
113:        num_channels,     # NumChannels (Mono=1)
114:        sample_rate,      # SampleRate (예: 24000)
115:        byte_rate,        # ByteRate
116:        block_align,      # BlockAlign
117:        bits_per_sample,  # BitsPerSample (예: 16)
118:        b"data",          # Subchunk2ID
119:        data_size         # Subchunk2Size
120:    )
121:    return header + audio_data
```

* **Line 85~92:** 원시 PCM 오디오 데이터에 표준 RIFF WAVE 헤더를 붙여 온전한 `.wav` 파일로 만들어주는 함수입니다.
* **Line 93~101:** 샘플 레이트(24000Hz), 비트 수(16bit), 채널 수(모노 1채널)를 바탕으로 바이트 레이트 및 파일 전체 크기(`chunk_size`)를 수학적으로 계산합니다.
* **Line 105~120:** `struct.pack`을 통해 표준 44바이트 WAV 규격 헤더를 리틀 엔디안(`<`) 바이너리로 생성합니다.
* **Line 121:** `header + audio_data` - 헤더 뒤에 원시 오디오 데이터를 붙여 유효한 WAV 바이너리를 반환합니다.

---

## 8. MIME 타입 파싱 함수 및 실행 진입점 (Line 125 ~ 164)

```python
125: def parse_audio_mime_type(mime_type: str) -> dict[str, int | None]:
...
135:     bits_per_sample = 16
136:     rate = 24000
...
139:     parts = mime_type.split(";")
140:     for param in parts:
...
142:         if param.lower().startswith("rate="):
...
149:         elif param.startswith("audio/L"):
...
155:     return {"bits_per_sample": bits_per_sample, "rate": rate}
156: 
157: 
158: if __name__ == "__main__":
159:     generate()
```

* **Line 125~155:** `parse_audio_mime_type` - Gemini API가 응답한 MIME 타입 문자열(예: `audio/L16;rate=24000`)을 파싱하여 샘플 레이트와 비트 심도를 딕셔너리로 반환합니다.
* **Line 158~159:** 파이썬 스크립트가 직접 실행(`__main__`)될 때 `generate()` 함수를 호출하여 음성 생성을 시작합니다.
