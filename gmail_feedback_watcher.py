import os
import base64
import time
import traceback
import json
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pymongo import MongoClient
from utils.llm_engine import analyze_transcript
from utils.pdf_generator import generate_pdf
import smtplib

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["SmartInterviewSystem"]
transcript_collection = db["Savedtranscripts"]

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

def authenticate_gmail():
    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not credentials_json:
        raise Exception("Missing GOOGLE_CREDENTIALS_JSON environment variable")

    creds = Credentials.from_authorized_user_info(json.loads(credentials_json), SCOPES)
    return build('gmail', 'v1', credentials=creds)

def check_feedback_requests(service):
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='subject:"Request Feedback" is:unread').execute()
    messages = results.get('messages', [])
    return messages

def get_sender_and_mark_read(service, msg_id):
    msg = service.users().messages().get(userId='me', id=msg_id, format='metadata', metadataHeaders=['From']).execute()
    headers = msg['payload']['headers']
    sender = next(h['value'] for h in headers if h['name'] == 'From')
    sender_email = sender.split('<')[-1].replace('>', '').strip()
    service.users().messages().modify(userId='me', id=msg_id, body={ 'removeLabelIds': ['UNREAD'] }).execute()
    return sender_email

def send_feedback(email):
    doc = transcript_collection.find_one({ "email": email })
    if not doc:
        print(f"❌ No transcript found for {email}")
        return

    transcript = doc["transcript_text"]
    os.makedirs("uploads", exist_ok=True)
    temp_path = f"uploads/{email.replace('@', '_at_')}.txt"
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(transcript)

    analysis = analyze_transcript(temp_path)
    if not analysis or "questions" not in analysis:
        print("❌ LLM analysis failed")
        return

    pdf_path = generate_pdf(email.split("@")[0], analysis)
    send_email_with_attachment(email, "Interview Feedback Report", "Here is your interview feedback.", pdf_path)
    print(f"✅ Feedback sent to {email}")

def send_email_with_attachment(to_email, subject, body, pdf_path):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with open(pdf_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=os.path.basename(pdf_path))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

def run_watcher():
    service = authenticate_gmail()
    print("📬 Watching for feedback requests...")

    while True:
        try:
            messages = check_feedback_requests(service)
            for msg in messages:
                msg_id = msg['id']
                sender_email = get_sender_and_mark_read(service, msg_id)
                print(f"📨 New request from: {sender_email}")
                send_feedback(sender_email)
        except Exception as e:
            print("❌ Error:", str(e))
            traceback.print_exc()

        time.sleep(3600)

if __name__ == '__main__':
    run_watcher()
