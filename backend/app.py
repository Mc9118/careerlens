
from flask import Flask, render_template, request, jsonify
from pypdf import PdfReader
from io import BytesIO
import re

app = Flask(__name__)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# Recognized technical skills and alternative names
SKILLS = {
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js"],
    "C++": ["c++"],
    "C#": ["c#"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "Bootstrap": ["bootstrap"],
    "Tailwind CSS": ["tailwind css", "tailwind"],
    "React": ["react", "react.js", "reactjs"],
    "Node.js": ["node.js", "nodejs"],
    "Express.js": ["express.js", "expressjs"],
    "Flask": ["flask"],
    "Django": ["django"],
    "FastAPI": ["fastapi"],
    "SQL": ["sql"],
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MongoDB": ["mongodb", "mongo db"],
    "SQLite": ["sqlite"],
    "REST API": ["rest api", "rest apis", "restful api", "restful apis"],
    "Git": ["git"],
    "GitHub": ["github"],
    "Linux": ["linux"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["microsoft azure", "azure"],
    "Google Cloud": ["google cloud", "gcp"],
    "Jenkins": ["jenkins"],
    "Terraform": ["terraform"],
    "Ansible": ["ansible"],
    "CI/CD": ["ci/cd", "continuous integration", "continuous deployment"],
    "HTML/CSS": ["html/css"],
    "PHP": ["php"],
    "C": ["c programming"],
    "Data Structures": ["data structures", "data structure"],
    "Algorithms": ["algorithms", "algorithm"],
    "OOP": ["object oriented programming", "oop"],
    "Machine Learning": ["machine learning", "ml"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Power BI": ["power bi"],
    "Excel": ["microsoft excel", "excel"],
}

# Check longer skill names first
SKILLS = dict(
    sorted(SKILLS.items(), key=lambda item: len(item[0]), reverse=True)
)


def extract_text_from_pdf(pdf_bytes):
    reader = PdfReader(BytesIO(pdf_bytes))

    if reader.is_encrypted:
        raise ValueError(
            "This PDF is password-protected. Upload an unlocked PDF."
        )

    return "\n".join(
        page.extract_text() or "" for page in reader.pages
    ).strip()


def extract_skills(text):
    """Find recognized technical skills in text."""
    found = set()
    text = text.lower()

    for skill, aliases in SKILLS.items():
        for alias in aliases:
            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(alias.lower())
                + r"(?![a-z0-9])"
            )

            if re.search(pattern, text):
                found.add(skill)
                break

    return found


def create_suggestions(missing_skills, score):
    learning_resources = {
        "Python": "Practice functions, lists, dictionaries, and small projects.",
        "Flask": "Build routes, REST APIs, and connect a database.",
        "SQL": "Practice SELECT, JOIN, GROUP BY, and CRUD queries.",
        "C++": "Practice variables, functions, classes, and data structures.",
        "Docker": "Learn images, containers, Dockerfiles, and port mapping.",
        "Kubernetes": "Learn Pods, Deployments, Services, and kubectl.",
        "AWS": "Practice IAM, EC2, S3, and basic cloud networking.",
        "Git": "Practice commits, branches, merges, and resolving conflicts.",
        "GitHub": "Practice repositories, pull requests, and collaboration.",
        "Linux": "Practice commands, file permissions, and processes.",
        "JavaScript": "Practice DOM manipulation, events, and fetch.",
        "React": "Learn components, props, state, and hooks.",
        "MongoDB": "Practice CRUD operations and aggregation.",
        "MySQL": "Practice joins, database design, and CRUD operations.",
        "HTML": "Practice semantic HTML and accessible page structure.",
        "CSS": "Learn Flexbox, Grid, and responsive web design.",
        "Node.js": "Practice building server-side applications.",
        "REST API": "Build and test REST endpoints.",
        "PostgreSQL": "Practice SQL queries and relational database design.",
        "CI/CD": "Build an automated testing and deployment workflow.",
        "Terraform": "Learn providers, resources, variables, and state.",
        "Ansible": "Practice inventory files and playbooks.",
        "Jenkins": "Create a pipeline that builds and tests an application.",
        "Machine Learning": "Start with Python data handling and basic ML models.",
        "Data Structures": "Practice arrays, linked lists, stacks, queues, and trees.",
        "Algorithms": "Practice searching, sorting, and time complexity.",
    }

    suggestions = []
    roadmap = []

    for skill in missing_skills:
        recommendation = learning_resources.get(
            skill,
            f"Study the fundamentals of {skill} and build a small project."
        )

        suggestions.append(f"{skill}: {recommendation}")

        # Example priorities; these can later be customized
        # for different job roles.
        if skill in ["Docker", "Git", "Linux", "AWS"]:
            priority = "High"
        else:
            priority = "Medium"

        roadmap.append({
            "skill": skill,
            "priority": priority,
            "learning_goal": recommendation
        })

    if missing_skills:
        suggestions.insert(
            0,
            "Skills to develop: " + ", ".join(missing_skills) + "."
        )
        suggestions.append(
            "Add skills to your resume only after you have practiced them."
        )

    if score < 40:
        suggestions.append(
            "Review the job requirements and build relevant practical projects."
        )
    elif score < 70:
        suggestions.append(
            "Connect your existing skills to projects and practical achievements."
        )
    else:
        suggestions.append(
            "Review the full job requirements, not just keyword overlap."
        )

    return suggestions, roadmap


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/analyze-resume", methods=["POST"])
def analyze_resume():
    if "resume" not in request.files:
        return jsonify({
            "error": "Please upload your resume PDF."
        }), 400

    resume_file = request.files["resume"]
    job_description = request.form.get(
        "job_description", ""
    ).strip()

    if not resume_file.filename:
        return jsonify({
            "error": "Choose a PDF resume first."
        }), 400

    if not resume_file.filename.lower().endswith(".pdf"):
        return jsonify({
            "error": "Only PDF files are supported."
        }), 400

    if not job_description:
        return jsonify({
            "error": "Please paste the job description."
        }), 400

    pdf_bytes = resume_file.read(MAX_FILE_SIZE + 1)

    if len(pdf_bytes) > MAX_FILE_SIZE:
        return jsonify({
            "error": "The PDF must be 5 MB or smaller."
        }), 400

    try:
        resume_text = extract_text_from_pdf(pdf_bytes)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        return jsonify({
            "error": "We couldn't read this PDF. Please try another PDF."
        }), 400

    if not resume_text:
        return jsonify({
            "error": (
                "No readable text found. Try a text-based PDF "
                "rather than a scanned image."
            )
        }), 400

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    if not job_skills:
        return jsonify({
            "error": (
                "No recognized technical skills were found in the job "
                "description. Try including skills such as Python, "
                "SQL, Flask, or Docker."
            )
        }), 400

    matched = sorted(resume_skills & job_skills)
    missing = sorted(job_skills - resume_skills)

    score = round((len(matched) / len(job_skills)) * 100)

    # Generate both suggestions and the learning roadmap
    suggestions, roadmap = create_suggestions(missing, score)

    if len(resume_text.split()) < 150:
        suggestions.append(
            "Your extracted resume text is short. Check that your "
            "projects, experience, education, and skills are included."
        )

    return jsonify({
        "score": score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "suggestions": suggestions,
        "roadmap": roadmap,
        "note": (
            "This score measures recognized technical-skill overlap only. "
            "It is not an official ATS score and does not measure overall "
            "job suitability."
        )
    })


if __name__ == "__main__":
    app.run(debug=True)
