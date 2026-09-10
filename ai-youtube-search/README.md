# 🎬 YouTube AI 검색기 & 비디오 어시스턴트

유튜브 공식 웹 UI 레이아웃을 기반으로 구축된 지능형 유튜브 검색 및 분석 웹 서비스입니다. 
상단 검색창에 유튜브 링크를 입력하면 영상이 바로 임베드 재생되며, **Gemini 3.5 Transcribe**를 통해 타임스탬프 자막을 자동 추출하고, **Gemini 3.8 Flash**를 통해 영상 내용 질문 답변 및 원하는 장면으로의 자동 탐색(Jump to Timestamp)을 제공합니다.

---

## 🌟 주요 기능

1. **YouTube 정통 UI/UX 디자인**:
   - 상단 헤더: YouTube AI 로고 및 중앙 유튜브 링크 검색창
   - 불필요한 마이크, 만들기, 알림, 계정 아이콘을 제거한 깔끔한 레이아웃
2. **동적 비디오 플레이어 & 실시간 음향 조절**:
   - YouTube IFrame Player API 연동
   - 커스텀 음향 크기(볼륨 0~100%) 조절 슬라이더 및 음소거 토글
3. **Gemini 3.5 Transcribe STT**:
   - `yt-dlp` 및 `imageio-ffmpeg`로 고음질 오디오(MP3) 추출
   - `gemini-3.5-transcribe` 모델의 정밀 단어 타임스탬프(`word_timestamp=True`) 기반 전사
4. **내용 검색 & 즉시 영상 이동 (Seek & Play)**:
   - 영상에서 특정 키워드나 주제를 검색하면 가장 적합한 발언 시간대를 찾고, 해당 위치로 **비디오가 즉시 이동(`seekTo`)하여 자동 재생**
5. **Gemini 3.8 Flash 영상 질의응답 (Q&A)**:
   - 추출된 자막을 바탕으로 `gemini-3.8-flash` 모델이 사용자의 질문에 정확히 답변
   - 답변 내에 발화 시점 타임스탬프(`[MM:SS]`)가 버튼으로 포함되어, 클릭 시 해당 구간으로 즉시 점프 가능

---

## 📁 디렉터리 구성

```text
ai-youtube-search/
├── app.py                         # FastAPI 메인 웹 서버 (포트: 8001)
├── requirements.txt               # 의존성 목록
├── run.bat                        # 원클릭 실행 배치 파일
├── README.md                      # 프로젝트 설명서
├── services/
│   ├── audio_downloader.py        # 유튜브 오디오 다운로더 및 비디오 ID 추출
│   ├── gemini_stt.py              # Gemini 3.5 Transcribe 기반 자막/타임스탬프 추출
│   └── gemini_chat.py             # Gemini 3.8 Flash 기반 질의응답 및 시맨틱 검색
├── static/
│   └── downloads/                 # 추출된 오디오 파일 임시 저장소
└── templates/
    └── index.html                 # YouTube 레이아웃 UI & IFrame 연동
```

---

## 🚀 실행 방법

### 방법 1. 원클릭 실행 (배치 파일)
`run.bat` 파일을 더블 클릭하여 실행합니다.

### 방법 2. 터미널에서 실행
```bash
conda activate myenv
cd c:\AI-Native-Agent\GoogleAiStudio-Tutorial\ai-youtube-search
python app.py
```

서버가 가동되면 브라우저에서 **`http://localhost:8001`**에 접속하여 사용합니다.
