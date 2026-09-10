# 🎙️ YouTube Audio & Transcript Web Service

유튜브 영상의 링크(URL)를 입력하면 해당 영상의 고음질 오디오(MP3)를 추출하고, 최신 Google Gemini AI 모델(`gemini-3.6-flash`)을 통해 전체 음성을 타임스탬프, 줄글 텍스트 및 핵심 요약으로 자동 전사해주는 모던 웹 서비스입니다.

---

## 🌟 주요 기능

1. **원클릭 오디오 다운로드**: `yt-dlp` 및 `ffmpeg`를 연동하여 유튜브 영상에서 192kbps 고음질 MP3 음원 자동 추출
2. **Gemini 차세대 AI STT**: 최신 `gemini-3.6-flash` 모델을 통해 대용량/장시간 음원도 끊김 없이 정확하게 텍스트로 변환
3. **3가지 전사 뷰 제공**:
   - **타임스탬프 자막**: 구간별 `[분:초 - 분:초]` 타임스탬프가 포함된 자막 스크립트
   - **전체 줄글**: 타임스탬프 없이 자연스럽게 읽을 수 있는 전체 본문
   - **핵심 요약**: 전체 대화 및 내용을 3~5줄로 간결하게 요약
4. **웹 내장 오디오 플레이어**: 다운로드된 오디오를 웹 브라우저에서 즉시 재생 및 원본 MP3 다운로드
5. **결과 활용**: 클립보드 원클릭 복사 및 `TXT` 파일 저장 지원

---

## 📁 디렉터리 구성

```text
youtube-transcript-web/
├── app.py                     # FastAPI 메인 웹 서버
├── requirements.txt           # 필수 패키지 목록
├── run.bat                    # 윈도우 원클릭 실행 스크립트
├── services/
│   ├── downloader.py          # yt-dlp 기반 오디오 다운로더
│   └── transcriber.py         # Google Gemini GenAI 기반 음성 전사
├── static/
│   └── downloads/             # 추출된 오디오 파일 임시 저장소
└── templates/
    └── index.html             # 모던 반응형 웹 UI 대시보드
```

---

## 🚀 실행 방법

### 방법 1. 배치 파일 실행 (가장 간편)
`run.bat` 파일을 더블 클릭하여 실행합니다.

### 방법 2. 터미널 명령어로 직접 실행
```bash
# 콘다 가상환경 활성화 (필요한 경우)
conda activate myenv

# 디렉터리 이동
cd c:\AI-Native-Agent\GoogleAiStudio-Tutorial\youtube-transcript-web

# 서버 실행
python app.py
```

서버가 실행되면 브라우저를 열고 **`http://localhost:8000`**에 접속하여 사용합니다.

---

## ⚙️ 사전 환경 요구사항
* `GEMINI_API_KEY` 환경 변수가 설정되어 있어야 합니다.
