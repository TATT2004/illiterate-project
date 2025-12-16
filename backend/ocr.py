import pytesseract
from PIL import Image
import os

def ocr_image(filepath):
    img = Image.open(filepath)
    text = pytesseract.image_to_string(img, lang="chi_tra")
    return text.strip()