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

load_dotenv()

# Mongo Setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["SmartInterviewSystem"]
transcript_collection = db["Savedtranscripts"]

# Flask App
PORT = int(os.environ.get("PORT", 10000))
app = Flask(__name__, template_folder="templates")
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

# ✅ GET Transcript by Email
@app.route("/api/get-transcript")
def get_transcript():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "❌ Email is required"}), 400

    doc = transcript_collection.find_one({"email": email})
    if not doc or "transcript_text" not in doc:
        return jsonify({"error": f"❌ No transcript found for {email}"}), 404

    return jsonify({"transcript": doc["transcript_text"]})

# ✅ Send Feedback + PDF
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

        doc = transcript_collection.find_one({"email": email})
        if not doc or "transcript_text" not in doc:
            return jsonify({"error": f"❌ No transcript found for {email}"}), 404

        # Save to file
        os.makedirs("uploads", exist_ok=True)
        temp_path = f"uploads/{email.replace('@', '_at_')}.txt"
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(doc["transcript_text"])

        # Analyze
        analysis = analyze_transcript(temp_path)
        print("📦 LLM RESPONSE:", analysis)

        if not analysis or "questions" not in analysis:
            return jsonify({
                "error": "❌ LLM analysis failed",
                "details": analysis.get("error", "Unknown"),
                "exception": analysis.get("exception", ""),
                "raw_response": analysis.get("raw_response", "")
            }), 500

        # Generate PDF
        pdf_path = generate_pdf(email.split("@")[0], analysis)

        # Email it
        send_email_with_attachment(email, subject, message, pdf_path, room_id)

        return jsonify({"success": True, "message": f"✅ Feedback sent to {email}"})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"🔥 Internal Server Error: {str(e)}"}), 500

# ✅ Send Result: Selected
@app.route("/api/finalize-success", methods=["POST"])
def finalize_success():
    data = request.json
    email = data.get("email")
    message = data.get("message", "🎉 Congratulations! You have been selected.")
    room_id = data.get("roomId", "N/A")
    return send_result_email(email, message, "Smart Interview Result", room_id)

# ✅ Send Result: Not Selected
@app.route("/api/finalize-failure", methods=["POST"])
def finalize_failure():
    data = request.json
    email = data.get("email")
    message = data.get("message", "🙏 Thank you for your time. Unfortunately, not selected.")
    room_id = data.get("roomId", "N/A")
    return send_result_email(email, message, "Smart Interview Result", room_id)

# 🔧 Email without attachment
def send_result_email(to_email, message, subject, room_id):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")

        if not sender_email or not sender_password:
            raise Exception("Missing SMTP credentials")

        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(f"{message}\n\n📌 Room ID: {room_id}\n📝 Smart Interview System")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return jsonify({"message": f"📧 Result sent to {to_email}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔧 Email with PDF
def send_email_with_attachment(to_email, subject, body, pdf_path, room_id):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        raise Exception("Missing SMTP credentials")

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(f"{body}\n\n📌 Room ID: {room_id}\n📝 Feedback Report Attached.")

    with open(pdf_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=os.path.basename(pdf_path))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        print(f"📧 Feedback sent to {to_email}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
