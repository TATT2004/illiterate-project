import requests
import base64

GOOGLE_API_KEY = ""

def text_to_speech(text, output_path):
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_API_KEY}"

    body = {
        "input": {"text": text},
        "voice": {
            "languageCode": "zh-TW",
            "ssmlGender": "NEUTRAL"
        },
        "audioConfig": {
            "audioEncoding": "MP3"
        }
    }

    res = requests.post(url, json=body).json()
    audio = base64.b64decode(res["audioContent"])

    with open(output_path, "wb") as f:
        f.write(audio)
