"""
main.py  —  CVScope FastAPI Backend (v2)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from utils import extract_text, extract_skills_detailed, match_skills, calculate_similarity, warmup_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm all NLP models at startup so the first request is fast."""
    warmup_models()
    yield


app = FastAPI(title="CVScope API", version="2.0", lifespan=lifespan)

# CORS — allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "CVScope Backend v2 Running", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


# ── Main analysis route ───────────────────────────────────────────────────────
@app.post("/analyze")
async def analyze(resume: UploadFile, job_description: str = Form(...)):
    """
    POST multipart/form-data:
      resume          — PDF or DOCX file
      job_description — plain text string

    Returns:
      match_percentage     — final weighted score (0–100)
      resume_skills        — extracted skills from resume
      job_skills           — extracted skills from JD
      matched_skills       — JD skills found in resume
      missing_skills       — JD skills NOT found in resume
      similarity_breakdown — skill_match_score, text_similarity_score, final_score
            resume_skill_details — explainability payload (confidence + sources + sections)
            job_skill_details    — explainability payload (confidence + sources + sections)
    """
    try:
        # ── Validate file type ────────────────────────────────────────────────
        if not resume.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")

        ext = resume.filename.lower().split(".")[-1]
        if ext not in ("pdf", "docx"):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '.{ext}'. Please upload PDF or DOCX."
            )

        # ── Extract raw text ──────────────────────────────────────────────────
        resume_text = extract_text(resume)
        if not resume_text.strip():
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from resume. Is the PDF image-based / scanned?"
            )

        jd_text = job_description.strip()
        if not jd_text:
            raise HTTPException(status_code=400, detail="Job description is empty")

        # ── Extract skills (with explainability) ─────────────────────────────
        resume_extraction = extract_skills_detailed(resume_text, doc_type="resume")
        jd_extraction = extract_skills_detailed(jd_text, doc_type="job_description")

        resume_skills = resume_extraction.skills
        jd_skills = jd_extraction.skills

        # ── Match skills ──────────────────────────────────────────────────────
        match_result = match_skills(resume_skills, jd_skills)

        # ── Score ─────────────────────────────────────────────────────────────
        breakdown = calculate_similarity(
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            resume_text=resume_text,
            jd_text=jd_text,
            jd_skill_weights=jd_extraction.confidence_by_skill,
        )

        return {
            "match_percentage": breakdown["final_score"],
            "resume_skills": resume_skills,
            "job_skills": jd_skills,
            "matched_skills": match_result.matched,
            "missing_skills": match_result.missing,
            "similarity_breakdown": breakdown,
            "resume_skill_details": resume_extraction.details,
            "job_skill_details": jd_extraction.details,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
