"""
main.py  —  CVScope FastAPI Backend (v3)
==========================================
API routes:
  GET  /           health check
  GET  /health     lightweight ping
  POST /analyze    full resume × job-description analysis

Response fields (POST /analyze):
  match_percentage        — final weighted score 0–100
  resume_skills           — list of canonical skill names from resume
  job_skills              — list of canonical skill names from JD
  matched_skills          — JD skills found in resume
  missing_skills          — JD skills NOT found in resume
  similarity_breakdown    — component scores + formula explanation
  resume_skill_details    — per-skill confidence + sources + sections
  job_skill_details       — per-skill confidence + sources + sections
  skill_categories        — resume skills grouped by category
  score_explanation       — plain-English list of reasons for the score
  skill_recommendations   — learning paths for missing skills (offline)
  role_matches            — top matching job roles for the resume

All processing is local. No external services are called.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from utils import (
    extract_text,
    extract_skills_detailed,
    match_skills,
    calculate_similarity,
    warmup_models,
    group_skills_by_category,
)
from recommendations import (
    get_skill_gap_recommendations,
    get_role_recommendations,
    generate_score_explanation,
)

# ── Startup ───────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm all NLP models at startup so the first request is not slow."""
    warmup_models()
    yield


app = FastAPI(title="CVScope API", version="3.0", lifespan=lifespan)

# CORS: allow all origins for local development.
# In production, replace "*" with the actual frontend origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health checks ─────────────────────────────────────────────────────────────

@app.get("/")
def home():
    return {"message": "CVScope Backend v3 Running", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


# ── Main analysis route ───────────────────────────────────────────────────────

MAX_FILE_BYTES = 10 * 1024 * 1024   # 10 MB


@app.post("/analyze")
async def analyze(resume: UploadFile, job_description: str = Form(...)):
    """
    POST multipart/form-data
      resume          — PDF or DOCX file (max 10 MB)
      job_description — plain text string

    Returns a JSON object. See module docstring for all fields.
    """
    try:
        # ── Validate file ────────────────────────────────────────────────────
        if not resume.filename:
            raise HTTPException(status_code=400, detail="No file uploaded.")

        ext = resume.filename.lower().rsplit(".", 1)[-1]
        if ext not in ("pdf", "docx"):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '.{ext}'. Please upload a PDF or DOCX file.",
            )

        raw_bytes = await resume.read()
        if len(raw_bytes) > MAX_FILE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large ({len(raw_bytes) // 1024} KB). Maximum allowed size is 10 MB.",
            )

        # ── Extract text ─────────────────────────────────────────────────────
        resume_text = extract_text(raw_bytes, filename=resume.filename)
        if not resume_text.strip():
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from the resume. Is the PDF image-based or scanned?",
            )

        jd_text = job_description.strip()
        if not jd_text:
            raise HTTPException(status_code=400, detail="Job description cannot be empty.")
        if len(jd_text) < 30:
            raise HTTPException(
                status_code=400,
                detail="Job description is too short. Please provide at least a few sentences.",
            )

        # ── Extract skills (with explainability) ─────────────────────────────
        resume_extraction = extract_skills_detailed(resume_text, doc_type="resume")
        jd_extraction = extract_skills_detailed(jd_text, doc_type="job_description")

        resume_skills: list[str] = resume_extraction.skills
        jd_skills: list[str] = jd_extraction.skills

        # ── Match skills ──────────────────────────────────────────────────────
        match_result = match_skills(resume_skills, jd_skills)

        # ── Similarity scoring ────────────────────────────────────────────────
        breakdown = calculate_similarity(
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            resume_text=resume_text,
            jd_text=jd_text,
            jd_skill_weights=jd_extraction.confidence_by_skill,
        )

        # ── Skill categorisation ──────────────────────────────────────────────
        skill_categories = group_skills_by_category(resume_skills)

        # ── Explainability ────────────────────────────────────────────────────
        score_explanation = generate_score_explanation(
            matched_skills=match_result.matched,
            missing_skills=match_result.missing,
            skill_match_score=breakdown["skill_match_score"],
            text_similarity_score=breakdown["text_similarity_score"],
            final_score=breakdown["final_score"],
        )

        # ── Recommendations ───────────────────────────────────────────────────
        skill_recommendations = get_skill_gap_recommendations(match_result.missing)

        # ── Role matching ─────────────────────────────────────────────────────
        role_matches = get_role_recommendations(resume_skills)

        return {
            "match_percentage": breakdown["final_score"],
            "resume_skills": resume_skills,
            "job_skills": jd_skills,
            "matched_skills": match_result.matched,
            "missing_skills": match_result.missing,
            "similarity_breakdown": breakdown,
            "resume_skill_details": resume_extraction.details,
            "job_skill_details": jd_extraction.details,
            "skill_categories": skill_categories,
            "score_explanation": score_explanation,
            "skill_recommendations": skill_recommendations,
            "role_matches": role_matches,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
