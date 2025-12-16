import base64
import requests
from openai import OpenAI
import os

GOOGLE_API_KEY = ""
OPENAI_API_KEY = ""

client = OpenAI(api_key=OPENAI_API_KEY)

def google_stt(filepath):
    with open(filepath, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode("utf-8")

    url = f"https://speech.googleapis.com/v1/speech:recognize?key={GOOGLE_API_KEY}"

    body = {
        "config": {"encoding": "MP3", "languageCode": "zh-TW"},
        "audio": {"content": audio_b64}
    }

    res = requests.post(url, json=body).json()
    print("Google STT 回傳：", res)  # 加這一行

    # 若無 results，回傳錯誤
    if "results" not in res:
        raise ValueError(f"Google STT 辨識失敗：{res}")

    text = res["results"][0]["alternatives"][0]["transcript"]
    return text


def openai_explain(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是一位中文老師，用簡單話解釋詞語。"},
            {"role": "user", "content": f"請簡單解釋：{text}"}
        ]
    )
    return response.choices[0].message.content


def google_tts(text):
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_API_KEY}"

    body = {
        "input": {"text": text},
        "voice": {"languageCode": "zh-TW", "ssmlGender": "NEUTRAL"},
        "audioConfig": {"audioEncoding": "MP3"}
    }

    res = requests.post(url, json=body).json()

    audio_data = base64.b64decode(res["audioContent"])

    with open("explain.mp3", "wb") as f:
        f.write(audio_data)

    return "explain.mp3"


def process_audio(filepath):
    text = google_stt(filepath)
    explanation = openai_explain(text)
    audio_path = google_tts(explanation)

    return text, explanation, audio_path
