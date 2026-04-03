from fastapi import FastAPI, UploadFile, Form
from utils import extract_text, extract_skills
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

@app.get("/")
def home():
    return {"message": "SkillSync Backend Running"}

@app.post("/analyze")
async def analyze(resume: UploadFile, job_description: str = Form(...)):
    
    # Extract resume text
    resume_text = extract_text(resume)

    # Extract skills
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    # Matching
    matched = list(set(resume_skills) & set(jd_skills))
    missing = list(set(jd_skills) - set(resume_skills))

    # Similarity score
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, job_description])
    score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    match_percentage = round(score * 100, 2)

    return {
        "match_percentage": match_percentage,
        "resume_skills": resume_skills,
        "job_skills": jd_skills,
        "matched_skills": matched,
        "missing_skills": missing
    }