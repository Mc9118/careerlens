
from flask import Flask, render_template, request, jsonify
from pypdf import PdfReader
from pathlib import Path
from io import BytesIO
import re

app = Flask(__name__)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

STOP_WORDS = {
    "the", "and", "for", "with", "that", "this", "from",
    "are", "you", "your", "our", "will", "have", "has",
    "was", "were", "their", "they", "job", "work", "role",
    "required", "requirements", "candidate", "ability"
}


def extract_keywords(text):
    words = re.findall(r"[a-zA-Z][a-zA-Z+#.]*", text.lower())
    return {
        word for word in words
        if len(word) > 1 and word not in STOP_WORDS
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/analyze-resume", methods=["POST"])
def analyze_resume():
    if "resume" not in request.files:
        return jsonify({"error": "Please upload your resume PDF."}), 400

    resume_file = request.files["resume"]
    job_description = request.form.get("job_description", "").strip()

    if not resume_file.filename:
        return jsonify({"error": "Choose a PDF resume first."}), 400

    if not resume_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    if not job_description:
        return jsonify({"error": "Please paste the job description."}), 400

    pdf_bytes = resume_file.read(MAX_FILE_SIZE + 1)

    if len(pdf_bytes) > MAX_FILE_SIZE:
        return jsonify({"error": "The PDF must be 5 MB or smaller."}), 400

    try:
        reader = PdfReader(BytesIO(pdf_bytes))

        if reader.is_encrypted:
            return jsonify({
                "error": "This PDF is password-protected. Upload an unlocked PDF."
            }), 400

        resume_text = "\n".join(
            page.extract_text() or "" for page in reader.pages
        ).strip()

    except Exception:
        return jsonify({
            "error": "We couldn't read this PDF. Please try another PDF."
        }), 400

    if not resume_text:
        return jsonify({
            "error": "No readable text found. Try a text-based PDF rather than a scanned image."
        }), 400

    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_description)

    if not job_keywords:
        return jsonify({
            "error": "The job description doesn't contain enough readable keywords."
        }), 400

    matched = sorted(resume_keywords & job_keywords)
    missing = sorted(job_keywords - resume_keywords)

    score = round((len(matched) / len(job_keywords)) * 100)

    suggestions = []

    if missing:
        suggestions.append(
            "Review the missing keywords and add relevant ones where they truthfully reflect your experience."
        )

    if score < 40:
        suggestions.append(
            "Tailor your skills and experience sections more closely to the job requirements."
        )
    elif score < 70:
        suggestions.append(
            "Improve alignment by highlighting relevant projects, tools, and achievements."
        )
    else:
        suggestions.append(
            "Your keyword alignment looks promising. Check that your experience and achievements are clearly explained."
        )

    if len(resume_text.split()) < 150:
        suggestions.append(
            "Your resume text is quite short. Make sure your relevant experience, projects, and education are included."
        )

    return jsonify({
        "score": score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "suggestions": suggestions,
        "note": "This is a basic keyword-match estimate, not an official ATS score."
    })


if __name__ == "__main__":
    app.run(debug=True)
