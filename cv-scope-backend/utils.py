import pdfplumber
import docx
import spacy
from skill_db import SKILLS

nlp = spacy.load("en_core_web_sm")

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

def extract_skills(text):
    text = text.lower()
    found = set()

    for skill, variants in SKILLS.items():
        for v in variants:
            if v in text:
                found.add(skill)

    return list(found)