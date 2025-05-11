# send_request.py
import requests

url = "http://127.0.0.1:5000/api/analyze"
files = {"transcript": open("uploads/sample_interview_transcript.txt", "rb")}

res = requests.post(url, files=files)

with open("downloaded_feedback.pdf", "wb") as f:
    f.write(res.content)

print("✅ PDF downloaded as downloaded_feedback.pdf")
