const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
let img = new Image();

// 框選狀態
let startX, startY, endX, endY;
let selecting = false;

// 語音網址
let ocrAudioUrl = "";
let explainAudioUrl = "";

// 歷史紀錄
let historyRecords = [];

// 原始圖片尺寸
let imgNaturalWidth = 0;
let imgNaturalHeight = 0;

// ===== 工具：取得 Canvas 繪圖座標 =====
function getCanvasPos(e) {
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;

  return {
    x: (e.clientX - rect.left) * scaleX,
    y: (e.clientY - rect.top) * scaleY
  };
}

// ===== 載入圖片 =====
document.getElementById("imageInput").addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = () => {
    img.onload = () => {
      imgNaturalWidth = img.naturalWidth;
      imgNaturalHeight = img.naturalHeight;

      canvas.width = img.width;
      canvas.height = img.height;

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
    };
    img.src = reader.result;
  };
  reader.readAsDataURL(file);
});

// ===== 滑鼠框選 =====
canvas.addEventListener("mousedown", (e) => {
  const pos = getCanvasPos(e);
  startX = pos.x;
  startY = pos.y;
  selecting = true;
});

canvas.addEventListener("mousemove", (e) => {
  if (!selecting) return;
  const pos = getCanvasPos(e);
  endX = pos.x;
  endY = pos.y;

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(img, 0, 0);

  ctx.strokeStyle = "red";
  ctx.lineWidth = 2;
  ctx.strokeRect(startX, startY, endX - startX, endY - startY);
});

canvas.addEventListener("mouseup", () => selecting = false);

// ===== 傳送裁切 =====
function sendCrop() {
  const file = document.getElementById("imageInput").files[0];
  if (!file) return alert("請先選擇圖片");

  // 停止播放避免鎖檔
  const audio = document.getElementById("audio");
  audio.pause();
  audio.currentTime = 0;

  if ([startX, startY, endX, endY].includes(undefined)) {
    return alert("請先框選文字");
  }

  const x = Math.min(startX, endX);
  const y = Math.min(startY, endY);
  const w = Math.abs(endX - startX);
  const h = Math.abs(endY - startY);

  const scaleX = imgNaturalWidth / canvas.width;
  const scaleY = imgNaturalHeight / canvas.height;

  const fd = new FormData();
  fd.append("image", file);
  fd.append("x", Math.round(x * scaleX));
  fd.append("y", Math.round(y * scaleY));
  fd.append("w", Math.round(w * scaleX));
  fd.append("h", Math.round(h * scaleY));

  fetch("/upload-crop", { method: "POST", body: fd })
    .then(res => res.json())
    .then(data => {
      document.getElementById("ocrText").innerText = data.ocr_text;
      document.getElementById("explanation").innerText = data.explanation;

      ocrAudioUrl = data.ocr_audio_url;
      explainAudioUrl = data.explain_audio_url;

      addHistory(data);
    })
    .catch(() => alert("處理失敗，請再試一次"));
}

// ===== 播放 =====
function playOcrAudio() {
  if (!ocrAudioUrl) return;
  playAudio(ocrAudioUrl);
}

function playExplainAudio() {
  if (!explainAudioUrl) return;
  playAudio(explainAudioUrl);
}

function playAudio(url) {
  const audio = document.getElementById("audio");
  audio.src = url + "?t=" + Date.now();
  audio.play();
}

// ===== 歷史紀錄 =====
function addHistory(data) {
  const list = document.getElementById("historyList");
  list.querySelector(".empty")?.remove();

  historyRecords.unshift(data);
  renderHistory();
}

function renderHistory() {
  const list = document.getElementById("historyList");
  list.innerHTML = "";

  historyRecords.forEach((item, i) => {
    const div = document.createElement("div");
    div.className = "history-item";
    div.innerHTML = `
      <div class="history-title">
        <span>第 ${historyRecords.length - i} 筆</span>
        <div>
          <button class="small-voice-btn" onclick="playAudio('${item.ocr_audio_url}')">🔊</button>
          <button class="small-voice-btn" onclick="playAudio('${item.explain_audio_url}')">🧠</button>
        </div>
      </div>
      <div class="history-text"><b>文字：</b>${item.ocr_text}</div>
      <div class="history-text"><b>解釋：</b>${item.explanation}</div>
    `;
    list.appendChild(div);
  });
}
