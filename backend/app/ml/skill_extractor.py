import io
import re
from pathlib import Path

SKILLS = [
    "Python", "Java", "C", "C++", "JavaScript", "TypeScript", "HTML", "CSS",
    "React", "Node.js", "Django", "Flask", "FastAPI", "MySQL", "PostgreSQL",
    "MongoDB", "SQL", "Redis", "Pandas", "NumPy", "Matplotlib", "Machine Learning",
    "Deep Learning", "NLP", "Computer Vision", "Scikit-learn", "TensorFlow",
    "PyTorch", "AWS", "Azure", "Docker", "Kubernetes", "Git", "GitHub", "Linux",
    "Statistics", "Excel", "Networking", "Cybersecurity"
]

ALIASES = {
    "js": "JavaScript",
    "ecmascript": "JavaScript",
    "ts": "TypeScript",
    "node": "Node.js",
    "nodejs": "Node.js",
    "ml": "Machine Learning",
    "dl": "Deep Learning",
    "natural language processing": "NLP",
    "cv": "Computer Vision",
    "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "py": "Python",
}


def _key(value: str) -> str:
    return re.sub(r"[^a-z0-9+#]+", "", value.casefold())


def canonical_skill(value: str) -> str:
    key = _key(value)
    if key in {_key(skill) for skill in SKILLS}:
        return next(skill for skill in SKILLS if _key(skill) == key)
    for alias, skill in ALIASES.items():
        if _key(alias) == key:
            return skill
    return value.strip()


def _text(data: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        import fitz
        doc = fitz.open(stream=data, filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    if ext == ".docx":
        from docx import Document
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    return data.decode("utf-8", errors="ignore")

def extract_skills(data: bytes, filename: str):
    text = _text(data, filename)
    if not text.strip():
        raise ValueError("Resume contains no readable text")
    found = []
    for skill in SKILLS:
        variants = [skill] + [alias for alias, canonical in ALIASES.items() if canonical == skill]
        if any(re.search(r"(?<![a-z0-9+#])" + re.escape(variant) + r"(?![a-z0-9+#])", text, re.I) for variant in variants):
            found.append(skill)
    return found
