# app.py
from flask import Flask, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os

from utils.llm_engine import analyze_transcript
from utils.pdf_generator import generate_pdf

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "✅ Smart Interview LLM Analysis API running!"

@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        print("⚙️ Starting LLM analysis on sample_interview_transcript.txt")

        # Analyze using LLM
        analysis = analyze_transcript()

        # Generate PDF
        pdf_path = generate_pdf("candidate", analysis)

        print("✅ PDF generated:", pdf_path)

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, port=port)
