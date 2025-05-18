from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
import uuid
import traceback

from utils.llm_engine import analyze_transcript
from utils.pdf_generator import generate_pdf

load_dotenv()
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        file = request.files.get("transcript")
        if not file or file.filename == "":
            return jsonify({"error": "No transcript uploaded"}), 400

        if not file.filename.endswith(".txt"):
            return jsonify({"error": "Only .txt files are supported"}), 400

        # ✅ Save with a unique name to avoid conflicts
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        print(f"📄 Saved uploaded transcript to: {path}")

        # Analyze using the exact file
        analysis = analyze_transcript(path)

        # Check for errors from LLM
        if not isinstance(analysis, dict) or "questions" not in analysis:
            return jsonify({"error": "LLM analysis failed", "raw": analysis}), 500

        # Generate PDF report
        pdf_path = generate_pdf("candidate", analysis)
        print(f"✅ PDF generated at: {pdf_path}")

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
