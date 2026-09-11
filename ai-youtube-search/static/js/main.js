// ==========================================
// YouTube AI 검색기 & 비디오 어시스턴트 JS
// ==========================================

// 전역 상태 변수
let ytPlayer = null;
let isPlayerReady = false;
let currentVideoData = null;
let activeTab = "search";

// DOM 요소 참조
const searchForm = document.getElementById("search-form");
const urlInput = document.getElementById("url-input");
const pasteBtn = document.getElementById("paste-btn");
const searchBtn = document.getElementById("search-btn");

const welcomeView = document.getElementById("welcome-view");
const loadingBar = document.getElementById("loading-bar");
const loadingTitle = document.getElementById("loading-title");
const loadingDesc = document.getElementById("loading-desc");
const playerContainer = document.getElementById("player-container");

const videoTitle = document.getElementById("video-title");
const videoUploader = document.getElementById("video-uploader");
const videoDuration = document.getElementById("video-duration");
const downloadMp3Link = document.getElementById("download-mp3-link");
const copyAllBtn = document.getElementById("copy-all-btn");
const copyBtnLabel = document.getElementById("copy-btn-label");

const muteBtn = document.getElementById("mute-btn");
const volumeIcon = document.getElementById("volume-icon");
const volumeSlider = document.getElementById("volume-slider");
const volumeLabel = document.getElementById("volume-label");

// 탭 요소들
const tabSearch = document.getElementById("tab-search");
const tabChat = document.getElementById("tab-chat");
const tabTranscript = document.getElementById("tab-transcript");
const panelSearch = document.getElementById("panel-search");
const panelChat = document.getElementById("panel-chat");
const panelTranscript = document.getElementById("panel-transcript");

const contentSearchForm = document.getElementById("content-search-form");
const contentQuery = document.getElementById("content-query");
const searchResultsBox = document.getElementById("search-results-box");

const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatMessages = document.getElementById("chat-messages");
const chatSubmitBtn = document.getElementById("chat-submit-btn");

const transcriptList = document.getElementById("transcript-list");
const segCount = document.getElementById("seg-count");

// 클립보드 붙여넣기
if (pasteBtn && urlInput) {
  pasteBtn.addEventListener("click", async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) urlInput.value = text;
    } catch (e) {
      console.warn("Clipboard access denied", e);
    }
  });
}

// YouTube IFrame Player 로드 및 초기화
function loadYouTubeVideo(videoId) {
  if (!window.YT || !window.YT.Player) {
    // API 아직 로드 전일 경우 대기 후 재시도
    setTimeout(() => loadYouTubeVideo(videoId), 300);
    return;
  }

  if (ytPlayer && ytPlayer.loadVideoById) {
    ytPlayer.loadVideoById(videoId);
    ytPlayer.playVideo();
  } else {
    ytPlayer = new YT.Player("youtube-iframe", {
      videoId: videoId,
      playerVars: {
        autoplay: 1,
        modestbranding: 1,
        rel: 0,
        controls: 1,
      },
      events: {
        onReady: (event) => {
          isPlayerReady = true;
          event.target.playVideo();
          updateVolumeUI(event.target.getVolume());
        }
      }
    });
  }
}

// 타임스탬프로 점프 및 재생 (글로벌 윈도우 객체에 바인딩하여 동적 HTML 버튼에서도 호출 가능)
function seekToTime(seconds) {
  if (ytPlayer && ytPlayer.seekTo) {
    ytPlayer.seekTo(seconds, true);
    ytPlayer.playVideo();
  }
}
window.seekToTime = seekToTime;

// 볼륨 조절 슬라이더 이벤트
if (volumeSlider) {
  volumeSlider.addEventListener("input", (e) => {
    const vol = parseInt(e.target.value, 10);
    if (ytPlayer && ytPlayer.setVolume) {
      if (ytPlayer.isMuted()) ytPlayer.unMute();
      ytPlayer.setVolume(vol);
    }
    updateVolumeUI(vol);
  });
}

// 음소거 토글
if (muteBtn) {
  muteBtn.addEventListener("click", () => {
    if (!ytPlayer) return;
    if (ytPlayer.isMuted()) {
      ytPlayer.unMute();
      const vol = ytPlayer.getVolume() || 80;
      if (volumeSlider) volumeSlider.value = vol;
      updateVolumeUI(vol);
    } else {
      ytPlayer.mute();
      updateVolumeUI(0);
    }
  });
}

function updateVolumeUI(vol) {
  if (volumeLabel) volumeLabel.innerText = `${vol}%`;
  if (!volumeIcon) return;
  if (vol === 0) {
    volumeIcon.className = "fa-solid fa-volume-xmark text-sm text-red-400";
  } else if (vol < 50) {
    volumeIcon.className = "fa-solid fa-volume-low text-sm";
  } else {
    volumeIcon.className = "fa-solid fa-volume-high text-sm";
  }
}

// 탭 전환 핸들러
function setTab(tab) {
  activeTab = tab;
  const tabs = [
    { key: "search", btn: tabSearch, panel: panelSearch },
    { key: "chat", btn: tabChat, panel: panelChat },
    { key: "transcript", btn: tabTranscript, panel: panelTranscript }
  ];

  tabs.forEach(t => {
    if (!t.btn || !t.panel) return;
    if (t.key === tab) {
      t.btn.className = "flex-1 py-3 px-2 text-center text-blue-400 border-b-2 border-blue-500 transition cursor-pointer flex items-center justify-center gap-1.5 font-bold";
      t.panel.classList.remove("hidden");
    } else {
      t.btn.className = "flex-1 py-3 px-2 text-center text-slate-400 hover:text-white transition cursor-pointer flex items-center justify-center gap-1.5";
      t.panel.classList.add("hidden");
    }
  });
}
window.setTab = setTab;

if (tabSearch) tabSearch.addEventListener("click", () => setTab("search"));
if (tabChat) tabChat.addEventListener("click", () => setTab("chat"));
if (tabTranscript) tabTranscript.addEventListener("click", () => setTab("transcript"));

// 초 -> mm:ss 변환
function formatTime(sec) {
  if (!sec) return "0:00";
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${s < 10 ? '0' : ''}${s}`;
}

// 메인 검색창 폼 제출 (URL 입력 및 분석 시작)
if (searchForm) {
  searchForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const url = urlInput.value.trim();
    if (!url) return;

    // UI 상태 전환
    if (welcomeView) welcomeView.classList.add("hidden");
    if (playerContainer) playerContainer.classList.remove("hidden");
    if (loadingBar) loadingBar.classList.remove("hidden");
    if (searchBtn) searchBtn.disabled = true;

    if (loadingTitle) loadingTitle.innerText = "유튜브 영상 분석 및 음원 다운로드 중...";
    if (loadingDesc) loadingDesc.innerText = "오디오를 추출한 뒤 Gemini 3.5 Transcribe로 타임스탬프를 추출합니다.";

    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });
      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.error || "영상 분석에 실패했습니다.");
      }

      currentVideoData = data;

      // 비디오 플레이어 로드
      loadYouTubeVideo(data.video_id);

      // 메타데이터 표시
      if (videoTitle) videoTitle.innerText = data.title;
      if (videoUploader) videoUploader.innerHTML = `<i class="fa-regular fa-circle-user mr-1"></i>${data.uploader}`;
      if (videoDuration) videoDuration.innerHTML = `<i class="fa-regular fa-clock mr-1"></i>${formatTime(data.duration)}`;
      if (downloadMp3Link) {
        downloadMp3Link.href = `/downloads/${data.audio_filename}`;
        downloadMp3Link.download = `${data.title}.mp3`;
      }

      const cacheBadge = document.getElementById("cache-badge");
      if (cacheBadge) {
        if (data.from_cache) {
          cacheBadge.classList.remove("hidden");
        } else {
          cacheBadge.classList.add("hidden");
        }
      }

      // 자막 렌더링
      renderTranscripts(data.transcription?.segments || []);

      if (loadingBar) loadingBar.classList.add("hidden");
      setTab("search");

    } catch (err) {
      alert("오류 발생: " + err.message);
      if (loadingBar) loadingBar.classList.add("hidden");
    } finally {
      if (searchBtn) searchBtn.disabled = false;
    }
  });
}

// 전체 자막 렌더링
function renderTranscripts(segments) {
  if (!transcriptList) return;
  transcriptList.innerHTML = "";
  if (segCount) segCount.innerText = `${segments.length}개 구간`;

  if (!segments || !segments.length) {
    transcriptList.innerHTML = `<div class="text-slate-500 py-4 text-center">추출된 자막이 없습니다.</div>`;
    return;
  }

  segments.forEach((seg) => {
    const item = document.createElement("div");
    item.className = "flex items-start gap-2.5 p-2 rounded-xl hover:bg-yt-card cursor-pointer transition group";
    item.innerHTML = `
      <button class="bg-blue-600/20 text-blue-400 font-mono text-[11px] font-semibold px-2 py-0.5 rounded border border-blue-500/30 group-hover:bg-blue-600 group-hover:text-white transition shrink-0">
        ${seg.timestamp}
      </button>
      <span class="text-slate-300 group-hover:text-white text-xs leading-relaxed">${seg.text}</span>
    `;
    item.addEventListener("click", () => {
      seekToTime(seg.start);
    });
    transcriptList.appendChild(item);
  });
}

// 내용 검색 & 자동 점프 핸들러
if (contentSearchForm) {
  contentSearchForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = contentQuery.value.trim();
    if (!query || !currentVideoData) return;

    const btn = document.getElementById("content-search-btn");
    if (btn) {
      btn.disabled = true;
      btn.innerText = "검색 중...";
    }

    try {
      const res = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query,
          transcript: currentVideoData.transcription?.full_transcript || "",
          segments: currentVideoData.transcription?.segments || []
        })
      });
      const data = await res.json();
      const result = data.data;

      if (!searchResultsBox) return;

      if (result && result.found) {
        // 해당 위치로 자동 점프 및 재생!
        seekToTime(result.target_sec);

        searchResultsBox.innerHTML = `
          <div class="bg-emerald-950/40 border border-emerald-500/40 rounded-xl p-3 mb-3">
            <div class="text-xs text-emerald-400 font-semibold mb-1 flex items-center gap-1.5">
              <i class="fa-solid fa-circle-check"></i> 해당 위치로 자동 이동했습니다:
              <button onclick="seekToTime(${result.target_sec})" class="bg-emerald-600 text-white px-2 py-0.5 rounded text-xs ml-1 font-mono hover:bg-emerald-500 cursor-pointer">
                ${result.timestamp}
              </button>
            </div>
            <div class="text-xs text-slate-200 mt-1">${result.matched_text}</div>
          </div>
        `;

        // 매칭 목록 추가 렌더링
        if (result.matches && result.matches.length > 1) {
          searchResultsBox.innerHTML += `<div class="text-[11px] text-slate-400 font-semibold mb-1">다른 관련 구간:</div>`;
          result.matches.slice(1).forEach(m => {
            const div = document.createElement("div");
            div.className = "flex items-center justify-between bg-yt-card p-2 rounded-lg text-xs hover:bg-yt-hover cursor-pointer mb-1 border border-yt-border";
            div.innerHTML = `
              <span class="truncate pr-2 text-slate-300">${m.text}</span>
              <span class="bg-blue-600/20 text-blue-400 px-1.5 py-0.5 rounded font-mono text-[10px] shrink-0">${m.timestamp}</span>
            `;
            div.addEventListener("click", () => seekToTime(m.start));
            searchResultsBox.appendChild(div);
          });
        }

      } else {
        searchResultsBox.innerHTML = `
          <div class="text-center text-slate-400 text-xs py-8">
            <i class="fa-solid fa-triangle-exclamation text-amber-400 text-lg mb-1 block"></i>
            "${query}" 관련 내용을 찾지 못했습니다.
          </div>
        `;
      }

    } catch (err) {
      alert("검색 오류: " + err.message);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerText = "검색 & 점프";
      }
    }
  });
}

// Gemini 3.8 Flash 질의응답 핸들러
if (chatForm) {
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const question = chatInput.value.trim();
    if (!question || !currentVideoData) return;

    chatInput.value = "";
    if (chatSubmitBtn) chatSubmitBtn.disabled = true;

    // 사용자 메시지 추가
    appendChatMessage("user", question);

    // AI 로딩 버블 추가
    const loadingBubble = appendChatMessage("ai", `<i class="fa-solid fa-spinner animate-spin mr-1"></i> Gemini 3.8 Flash가 영상 내용을 분석 중입니다...`);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          transcript: currentVideoData.transcription?.full_transcript || "",
          question: question
        })
      });
      const data = await res.json();
      const answer = data.data.answer;

      // 타임스탬프를 클릭 가능한 점프 버튼으로 치환
      const formattedAnswer = answer.replace(/\[(\d{1,2}:\d{2})\]/g, (match, ts) => {
        const parts = ts.split(":");
        const sec = parseInt(parts[0], 10) * 60 + parseInt(parts[1], 10);
        return `<button onclick="seekToTime(${sec})" class="inline-flex items-center gap-1 bg-blue-600/30 text-blue-400 hover:bg-blue-600 hover:text-white px-1.5 py-0.2 rounded font-mono text-xs border border-blue-500/40 transition cursor-pointer">[${ts}]</button>`;
      });

      loadingBubble.innerHTML = `
        <div class="font-bold text-emerald-400 mb-1 flex items-center gap-1.5">
          <i class="fa-solid fa-robot"></i> Gemini 3.8 Flash
        </div>
        <div class="leading-relaxed text-slate-200 whitespace-pre-wrap">${formattedAnswer}</div>
      `;

    } catch (err) {
      loadingBubble.innerHTML = `<span class="text-red-400">답변 생성 중 오류가 발생했습니다.</span>`;
    } finally {
      if (chatSubmitBtn) chatSubmitBtn.disabled = false;
      if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  });
}

function appendChatMessage(sender, htmlContent) {
  if (!chatMessages) return null;
  const msg = document.createElement("div");
  if (sender === "user") {
    msg.className = "bg-blue-600/20 border border-blue-500/30 p-3 rounded-xl ml-6 text-slate-100";
    msg.innerHTML = `<div class="font-bold text-blue-400 mb-1">나의 질문</div><div>${htmlContent}</div>`;
  } else {
    msg.className = "bg-yt-card border border-yt-border p-3 rounded-xl mr-6 text-slate-200";
    msg.innerHTML = htmlContent;
  }
  chatMessages.appendChild(msg);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return msg;
}

// 전체 자막 복사
if (copyAllBtn) {
  copyAllBtn.addEventListener("click", async () => {
    if (!currentVideoData) return;
    const text = currentVideoData.transcription?.full_transcript || "";
    try {
      await navigator.clipboard.writeText(text);
      if (copyBtnLabel) copyBtnLabel.innerText = "복사 완료!";
      setTimeout(() => {
        if (copyBtnLabel) copyBtnLabel.innerText = "전체 자막 복사";
      }, 2000);
    } catch (e) {
      console.warn("Copy failed", e);
    }
  });
}
