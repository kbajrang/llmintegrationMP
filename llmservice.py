from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from utils.llm_engine import analyze_transcript
from utils.pdf_generator import generate_pdf
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return "✅ Interview PDF API is running!"

@app.route("/api/get-transcript")
def get_transcript():
    from pymongo import MongoClient
    MONGO_URI = os.getenv("MONGO_URI")
    client = MongoClient(MONGO_URI)
    db = client["SmartInterviewSystem"]
    transcript_collection = db["Savedtranscripts"]

    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email required"}), 400

    doc = transcript_collection.find_one({"email": email})
    if not doc or "transcript_text" not in doc:
        return jsonify({"error": f"No transcript found for {email}"}), 404

    return jsonify({"transcript": doc["transcript_text"]})


@app.route("/api/generate-report", methods=["POST"])
def generate_report():
    try:
        file = request.files.get("file")
        if not file or file.filename == "":
            return jsonify({"error": "No transcript file provided"}), 400

        filename = secure_filename(file.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        analysis = analyze_transcript(path)
        if not analysis or "questions" not in analysis:
            return jsonify({"error": "LLM analysis failed", "raw": analysis}), 500

        pdf_path = generate_pdf("feedback", analysis)
        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
