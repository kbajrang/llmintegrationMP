from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from utils.llm_engine import analyze_transcript
from utils.pdf_generator import generate_pdf
import os
import smtplib
from email.message import EmailMessage
import traceback
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["SmartInterviewSystem"]  # ✅ Correct DB name
transcript_collection = db["Savedtranscripts"]  # ✅ Correct collection

# Flask app setup
PORT = int(os.environ.get("PORT", 10000))
app = Flask(__name__, template_folder="templates")
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/send-feedback", methods=["POST"])
def send_feedback():
    try:
        data = request.json
        email = data.get("email")
        subject = data.get("subject", "Smart Interview Feedback Report")
        message = data.get("message", "Thank you for participating in the interview.")
        room_id = data.get("roomId", "N/A")

        if not email:
            return jsonify({"error": "❌ Email is required"}), 400

        # Fetch transcript from MongoDB
        doc = transcript_collection.find_one({"email": email})
        if not doc or "transcript_text" not in doc:
            return jsonify({"error": f"❌ No transcript found for {email}"}), 404

        transcript_text = doc["transcript_text"]

        # Save transcript to temporary .txt file
        os.makedirs("uploads", exist_ok=True)
        temp_path = f"uploads/{email.replace('@', '_at_')}.txt"
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        # Analyze with LLM
        analysis = analyze_transcript(temp_path)
        if not analysis or "questions" not in analysis:
            return jsonify({"error": "❌ LLM analysis failed", "raw": analysis}), 500

        # Generate PDF
        pdf_path = generate_pdf(email.split("@")[0], analysis)

        # Send Email
        send_email_with_attachment(email, subject, message, pdf_path, room_id)

        return jsonify({"success": True, "message": f"✅ Feedback sent to {email}"})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"🔥 Internal Server Error: {str(e)}"}), 500

def send_email_with_attachment(to_email, subject, body, pdf_path, room_id):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        raise Exception("SMTP credentials not set in environment variables")

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    content = f"""{body}

📌 Interview Room ID: {room_id}

📝 Attached is your feedback report. We appreciate your time and effort.
"""
    msg.set_content(content)

    with open(pdf_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=os.path.basename(pdf_path))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        print(f"📧 Sent feedback to {to_email}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)