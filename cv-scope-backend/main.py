from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from utils import extract_text, extract_skills
from utils import calculate_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import extract_text, extract_skills, calculate_similarity, match_skills

app = FastAPI()

# ✅ CORS FIX (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Health check route
@app.get("/")
def home():
    return {"message": "SkillSync Backend Running"}


# ✅ MAIN ANALYSIS ROUTE
@app.post("/analyze")
async def analyze(resume: UploadFile, job_description: str = Form(...)):
    try:
        # Extract resume text
        resume_text = extract_text(resume)

        if not resume_text:
            return {"error": "Could not extract text from resume"}

        # Extract skills
        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(job_description)

        matched, missing = match_skills(resume_skills, jd_skills)

        match_percentage = calculate_similarity(resume_skills, jd_skills)

        return {
            "match_percentage": match_percentage,
            "resume_skills": resume_skills,
            "job_skills": jd_skills,
            "matched_skills": matched,
            "missing_skills": missing
        }

    except Exception as e:
        return {
            "error": str(e)
        }