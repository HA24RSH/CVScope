import pdfplumber
import docx
import re
from skill_db import SKILLS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher


# 📄 Extract text from file
def extract_text(file):
    if file.filename.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    elif file.filename.endswith(".docx"):
        doc = docx.Document(file.file)
        return " ".join([p.text for p in doc.paragraphs])

    return ""


# 🔧 Normalize text
def normalize(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9#+\. ]', ' ', text)
    return text


# 🧠 Extract skills (FINAL STABLE VERSION)
def extract_skills(text):
    text = normalize(text)
    found = set()

    # 🔥 1. Extract from "Skills:" section (PRIMARY)
    skill_section_match = re.search(r'skills\s*[:\-]?\s*(.*)', text)

    if skill_section_match:
        skill_section = skill_section_match.group(1)

        raw_skills = re.split(r'[,\n]', skill_section)

        for skill in raw_skills:
            skill = skill.strip()

            if 2 < len(skill) < 30:
                found.add(skill)

    # 🔥 2. Controlled dynamic extraction
    tokens = re.findall(r'\b[a-zA-Z][a-zA-Z0-9\+\#\.]{2,}\b', text)

    STOPWORDS = {
        "and", "with", "using", "the", "for", "to", "of",
        "in", "on", "by", "a", "an", "is", "are",
        "develop", "build", "manage", "implement",
        "application", "applications", "system",
        "skills", "requirements", "overview",
        "maintain", "integration", "functionality",
        "database", "databases"
    }

    TECH_PATTERNS = [
        "js", "api", "db", "sql", "node", "react",
        "mongo", "firebase", "next", "angular",
        "python", "java", "php", "golang",
        "rust", "blockchain", "html", "css"
    ]

    for token in tokens:
        token = token.lower()

        if token in STOPWORDS:
            continue

        # Only keep if it looks like tech
        if any(pattern in token for pattern in TECH_PATTERNS):
            found.add(token)

    # 🔥 3. Final cleanup
    cleaned = []

    for s in found:
        if any(x in s for x in ["@", "+91", "http", "www"]):
            continue
        if len(s) < 2:
            continue

        cleaned.append(s)

    return list(set(cleaned))

# 🤖 ML similarity score
def calculate_similarity(resume_skills, jd_skills):
    if not jd_skills:
        return 0

    resume_text = " ".join(resume_skills)
    jd_text = " ".join(jd_skills)

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, jd_text])

    score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    return round(score * 100, 2)


# 🔍 Fuzzy match
def is_similar(a, b):
    return SequenceMatcher(None, a, b).ratio() > 0.7


def match_skills(resume_skills, jd_skills):
    matched = []
    missing = []

    for jd_skill in jd_skills:
        found_match = False

        for res_skill in resume_skills:
            if is_similar(jd_skill, res_skill):
                matched.append(jd_skill)
                found_match = True
                break

        if not found_match:
            missing.append(jd_skill)

    return matched, missing