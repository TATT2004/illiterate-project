from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from PIL import Image
import uuid

from ocr import ocr_image
from ai import explain_text
from tts import text_to_speech

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

UPLOAD = "uploads"
os.makedirs(UPLOAD, exist_ok=True)

@app.route("/")
def home():
    return send_from_directory("../frontend", "index.html")


@app.route("/upload-crop", methods=["POST"])
def upload_crop():
    img_file = request.files["image"]
    x = int(request.form["x"])
    y = int(request.form["y"])
    w = int(request.form["w"])
    h = int(request.form["h"])

    # ✅ 每次請求使用唯一 ID，避免覆寫 / 檔案鎖定
    req_id = uuid.uuid4().hex

    img_path = os.path.join(UPLOAD, f"origin_{req_id}.png")
    crop_path = os.path.join(UPLOAD, f"crop_{req_id}.png")

    ocr_audio = os.path.join(UPLOAD, f"ocr_{req_id}.mp3")
    explain_audio = os.path.join(UPLOAD, f"explain_{req_id}.mp3")

    img_file.save(img_path)

    # ✅ 用 with 確保檔案關閉（Windows 很重要）
    with Image.open(img_path) as im:
        cropped = im.crop((x, y, x + w, y + h))
        cropped.save(crop_path)

    ocr_text = ocr_image(crop_path)
    explanation = explain_text(ocr_text)

    text_to_speech(ocr_text, ocr_audio)
    text_to_speech(explanation, explain_audio)

    return jsonify({
        "ocr_text": ocr_text,
        "explanation": explanation,
        "ocr_audio_url": f"/audio/ocr_{req_id}.mp3",
        "explain_audio_url": f"/audio/explain_{req_id}.mp3"
    })

@app.route("/audio/<filename>")
def audio(filename):
    return send_from_directory(UPLOAD, filename)


if __name__ == "__main__":
    app.run(debug=True)
