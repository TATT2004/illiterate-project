import tkinter as tk
from tkinter import filedialog
import pyttsx3

def speak():
    text = entry.get().strip()
    if not text:
        return
    
    engine = pyttsx3.init()  # 每次重新初始化避免無反應
    engine.say(text)
    engine.runAndWait()

def load_txt():
    filepath = filedialog.askopenfilename(
        filetypes=[("文字檔 (*.txt)", "*.txt"), ("所有檔案", "*.*")]
    )
    if filepath:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        entry.delete(0, tk.END)         # 清除舊內容
        entry.insert(0, content)        # 將 TXT 內容塞進輸入框
        speak()                         # 讀取並朗讀

window = tk.Tk()
window.title("簡易文字轉語音機器")

entry = tk.Entry(window, width=40)
entry.pack(padx=10, pady=10)

btn = tk.Button(window, text="開始朗讀", command=speak)
btn.pack(pady=5)

load_btn = tk.Button(window, text="上傳 TXT 檔並朗讀", command=load_txt)
load_btn.pack(pady=5)

window.mainloop()
