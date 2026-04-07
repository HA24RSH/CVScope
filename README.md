CvScope — Resume Analysis & Skill Matching (FastAPI + React)
CvScope is a full-stack web app that compares a candidate resume (PDF/DOCX) against a job description and returns:

Match percentage (skills coverage + section-weighted TF‑IDF cosine similarity)
Extracted resume skills and job skills
Matched skills and missing skills
Similarity breakdown (skill match vs text similarity)
Explainable skill extraction details (confidence + sources)
Features
Upload resume (PDF / DOCX)
Paste job description
Skill extraction (spaCy PhraseMatcher + NER + noun chunks + YAKE keyphrases)
Skill matching (fuzzy match)
Match percentage (weighted skills + text similarity)
React UI to display results
Tech Stack
Backend

FastAPI (API server): main.py
PDF parsing: pdfplumber
DOCX parsing: python-docx
Similarity: scikit-learn (TF‑IDF + cosine similarity)
NLP: spaCy (en_core_web_sm)
Fuzzy matching: rapidfuzz
Keyphrases (unknown skills): YAKE
Upload handling: python-multipart (required by FastAPI for form/file uploads)
Frontend

React (Create React App): package.json
Project Structure
Backend

main.py — FastAPI app, routes
utils.py — text extraction, skill extraction, similarity, fuzzy matching
skill_db.py — optional skill aliases (currently imported but not actively used by the extractor)
Resume.csv — sample data (optional)
Frontend

UploadForm.js — posts resume + job description to backend
ResultCard.js — renders results
Prerequisites
Python installed (any recent 3.x version should work)
Node.js + npm installed
Setup and Run (Windows, step-by-step)
You must run BOTH backend and frontend at the same time.

1) Start the backend (FastAPI)
Open a terminal (PowerShell) and run:

If you already have a virtual environment folder there (for example, named venv), activate it. Otherwise create one (recommended: .venv):

Create a venv (recommended):

Activate it:

If activation is blocked, run this once in the same terminal and retry activation:

Upgrade pip and install dependencies:

Start the backend server:

Check it in the browser:

http://127.0.0.1:8000/
You should see:

{"message":"CVScope Backend v2 Running","status":"ok"}
Important note about the common “uvicorn not recognized” error:

If you run uvicorn main:app --reload and get “uvicorn is not recognized”, use python -m uvicorn ... as shown above. That ensures you’re using the uvicorn installed in your currently activated venv.
2) Start the frontend (React)
Open a second terminal and run:

Open:

http://localhost:3000/
How the App Works
Frontend → Backend call
The frontend posts a multipart form request to:

http://127.0.0.1:8000/analyze
This is hardcoded in UploadForm.js. If you change the backend host/port, update that URL.

Backend API
Health check

GET /
Response example:
{"message":"SkillSync Backend Running"}
Analyze endpoint

POST /analyze
Content-Type: multipart/form-data
Form fields:
resume: file (PDF or DOCX)
job_description: string
Response JSON fields:

match_percentage: number (0–100)
resume_skills: array of strings
job_skills: array of strings
matched_skills: array of strings
missing_skills: array of strings
similarity_breakdown: object (skill_match_score, text_similarity_score, final_score, …)
resume_skill_details: array (skill, confidence, sources, sections, surface_forms)
job_skill_details: array (skill, confidence, sources, sections, surface_forms)
Where it’s implemented:

Route: main.py
Logic: utils.py
Troubleshooting
Backend won’t start: “uvicorn is not recognized”

Activate the venv first, then run:
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
Backend error about multipart/form-data

Install python-multipart in the same venv you’re running:
python -m pip install python-multipart
PowerShell: running scripts is disabled

Run in that terminal:
Set-ExecutionPolicy -Scope Process Bypass
Then activate your venv again.
Frontend shows “Failed to connect to backend”

Confirm backend is running at http://127.0.0.1:8000/
Confirm the frontend is using the same URL in UploadForm.js
Make sure port 8000 isn’t blocked/in use.
Port already in use

Change ports when starting:
Backend: use a different --port
Frontend: React will usually prompt to use another port automatically
Notes / Current Behavior
Skill extraction uses a multi-pass NLP pipeline in utils.py:
- PhraseMatcher (taxonomy/aliases) + NER fallback + noun chunks + YAKE keyphrases
Scoring combines:
- Skill coverage (confidence-weighted when available)
- Section-weighted TF‑IDF cosine similarity
Fuzzy matching uses rapidfuzz token_sort_ratio