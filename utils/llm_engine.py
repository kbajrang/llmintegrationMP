import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

TRANSCRIPT_PATH = os.path.join("uploads", "sample_interview_transcript.txt")

def analyze_transcript():
    if not os.path.exists(TRANSCRIPT_PATH):
        return {"error": f"Transcript not found at {TRANSCRIPT_PATH}"}

    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        transcript = f.read()

    prompt = f"""
You are a professional technical interview evaluator AI.

From the transcript below, extract each **question and answer pair**. For every pair, return a **JSON object** with:
- "question": full question text
- "answer": full candidate response
- "feedback": detailed review of the answer quality
- "score": rate out of 10 (as string like "8/10")
- "suggestion": what could have been done better (or say "Perfect!" if applicable)

At the end, also return a key:
- "summary_table": a list of [Question X, Score] for every question.

⚠ Return as a single JSON object with:
- "questions": a list of individual Q&A evaluations
- "summary_table": list of [question label, score]

Transcript:
\"\"\"
{transcript}
\"\"\"
"""

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost"
    }

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 6096,  # ✅ Increase this to 6000–8000 if your model/plan supports it
        "temperature": 0.7,  # Optional: slight creativity
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    content = response.json()['choices'][0]['message']['content']

    try:
        return json.loads(content)
    except Exception as e:
        return {"error": "Failed to parse JSON", "raw_response": content, "exception": str(e)}
