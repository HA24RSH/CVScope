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
    doc = nlp(text.lower())
    tokens = [token.text for token in doc]

    found = set()
    for skill in SKILLS:
        if skill in text.lower():
            found.add(skill)

    return list(found)