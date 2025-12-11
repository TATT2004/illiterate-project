import tkinter as tk
from tkinter import filedialog
import requests
import base64
from openai import OpenAI
import os

# -------------------------
# API Keys
# -------------------------
GOOGLE_API_KEY = ""
OPENAI_API_KEY = ""

client = OpenAI(api_key=OPENAI_API_KEY)

# ------------------------------------------------
# 選擇 MP3 並進行語音轉文字
# ------------------------------------------------
def choose_mp3():
    filepath = filedialog.askopenfilename(
        filetypes=[("音訊檔案", "*.mp3;*.wav;*.m4a;*.mp4"), ("All files", "*.*")]
    )
    if filepath:
        status_label.config(text="音檔讀取中...", fg="blue")
        transcribe_audio(filepath)


# ------------------------------------------------
# Google Speech-to-Text
# ------------------------------------------------
def transcribe_audio(filepath):
    with open(filepath, "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode("utf-8")

    url = f"https://speech.googleapis.com/v1/speech:recognize?key={GOOGLE_API_KEY}"

    body = {
        "config": {
            "encoding": "MP3",
            "languageCode": "zh-TW"
        },
        "audio": {
            "content": audio_base64
        }
    }

    response = requests.post(url, json=body)
    result = response.json()
    print(result)

    try:
        text = result["results"][0]["alternatives"][0]["transcript"]
        result_label.config(text="語音辨識：" + text)

        # OpenAI 解釋
        explain_text_openai(text)

    except:
        result_label.config(text="辨識失敗，請使用較清晰的音檔")
        status_label.config(text="請選擇音檔", fg="black")
        return


# ------------------------------------------------
# OpenAI AI 解釋（取代 Gemini）
# ------------------------------------------------
def explain_text_openai(input_text):
    status_label.config(text="AI 解釋中...", fg="green")

    prompt = f"請用非常簡單、淺顯易懂的中文解釋這段話或詞語：{input_text}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是一位中文老師，會用簡單的方式解釋詞語。"},
                {"role": "user", "content": prompt}
            ]
        )

        explanation = response.choices[0].message.content
        explanation_label.config(text="AI 解釋：" + explanation)

        speak_text(explanation)

    except Exception as e:
        explanation_label.config(text="AI 解釋失敗：" + str(e))

    status_label.config(text="請選擇音檔", fg="black")


# ------------------------------------------------
# Google TTS 播放
# ------------------------------------------------
def speak_text(text):
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_API_KEY}"

    body = {
        "input": {"text": text},
        "voice": {"languageCode": "zh-TW", "ssmlGender": "NEUTRAL"},
        "audioConfig": {"audioEncoding": "MP3"}
    }

    response = requests.post(url, json=body)
    data = response.json()

    audio_data = base64.b64decode(data["audioContent"])

    with open("explain.mp3", "wb") as f:
        f.write(audio_data)

    os.system("start explain.mp3")  # Windows 播放


# ------------------------------------------------
# Tkinter UI
# ------------------------------------------------
root = tk.Tk()
root.title("MP3 語音轉文字 + OpenAI 解釋 + TTS")
root.geometry("600x450")

status_label = tk.Label(root, text="請選擇音檔", font=("Arial", 14))
status_label.pack(pady=10)

choose_btn = tk.Button(root, text="選擇 MP3 檔案", font=("Arial", 16), command=choose_mp3)
choose_btn.pack(pady=10)

result_label = tk.Label(root, text="語音辨識：", font=("Arial", 14), wraplength=550)
result_label.pack(pady=20)

explanation_label = tk.Label(root, text="AI 解釋：", font=("Arial", 14), wraplength=550, justify="left")
explanation_label.pack(pady=20)

root.mainloop()
