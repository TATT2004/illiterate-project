from openai import OpenAI

# client = OpenAI(api_key="")

def explain_text(text):
    prompt = f"""
請用非常簡單、白話、適合不識字者理解的中文解釋下面的文字：
{text}
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是一位教不識字者認字的老師。"},
            {"role": "user", "content": prompt}
        ]
    )

    return res.choices[0].message.content.strip()
