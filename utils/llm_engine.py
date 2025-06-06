import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def analyze_transcript(transcript_path, model: str = "openai/gpt-3.5-turbo") -> dict:
    """Analyze a transcript file using the configured LLM service."""

    if not os.path.exists(transcript_path):
        return {"error": f"Transcript not found at {transcript_path}"}

    if not OPENROUTER_API_KEY:
        return {"error": "OPENROUTER_API_KEY not configured"}

    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()

    prompt = f"""
You are a top-tier AI trained to evaluate technical interviews for software engineers.

Your job is to analyze the following **interview transcript**, extract each **question and answer pair**, and return detailed structured feedback in JSON.

🔍 For each Q&A pair, return:
- "question": full question asked
- "answer": full candidate reply
- "feedback": clear, professional review covering correctness, clarity, depth, technical accuracy, and communication quality
- "score": number out of 10 (as string like "9/10")
- "suggestion": specific improvement tips (not just "Perfect!")

📊 Then, return a "summary_table":
- A list of short ["Topic", "Score"] rows for each question

⚠️ Format response as a valid JSON object:
{{
  "questions": [ ... ],
  "summary_table": [ ... ]
}}

🎯 Make feedback coaching-focused, specific, and varied (not generic praise).

Transcript:
\"\"\"
{transcript}
\"\"\"
"""

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 3000,
        "temperature": 0.8,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        return {
            "error": "Failed to analyze transcript",
            "exception": str(e),
            "raw_response": response.text if 'response' in locals() else "No response"
        }
