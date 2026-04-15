"""
main.py  —  CVScope FastAPI Backend (v2)
"""

from contextlib import asynccontextmanager
import importlib.metadata as _meta
import sys

from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from utils import extract_text, extract_skills_detailed, match_skills, calculate_similarity, warmup_models, ENABLE_YAKE
from recommendations import get_recommendations


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


# ── Environment info (for cross-machine debugging) ───────────────────────────
@app.get("/env")
def env_info():
    """
    Returns package versions and feature flags.
    Use this to confirm both machines have identical environments.
    Share with friend: GET http://127.0.0.1:8000/env
    """
    def _ver(pkg: str) -> str:
        try:
            return _meta.version(pkg)
        except Exception:
            return "not installed"

    return {
        "python": sys.version.split()[0],
        "packages": {
            "spacy":        _ver("spacy"),
            "pdfplumber":   _ver("pdfplumber"),
            "rapidfuzz":    _ver("rapidfuzz"),
            "scikit-learn": _ver("scikit-learn"),
            "yake":         _ver("yake"),
            "fastapi":      _ver("fastapi"),
            "uvicorn":      _ver("uvicorn"),
            "python-docx":  _ver("python-docx"),
        },
        "feature_flags": {
            "ENABLE_YAKE": ENABLE_YAKE,
        },
        "note": (
            "Share this output with collaborators to confirm identical environments. "
            "All 'packages' versions must match for deterministic skill extraction."
        ),
    }


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
      recommendations      — curated learning resources for each missing skill
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

        # ── Recommendations for missing skills ────────────────────────────────
        recommendations = get_recommendations(match_result.missing)

        return {
            "match_percentage": breakdown["final_score"],
            "resume_skills": resume_skills,
            "job_skills": jd_skills,
            "matched_skills": match_result.matched,
            "missing_skills": match_result.missing,
            "similarity_breakdown": breakdown,
            "resume_skill_details": resume_extraction.details,
            "job_skill_details": jd_extraction.details,
            "recommendations": recommendations,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")