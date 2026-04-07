CvScope — Resume Analysis & Skill Matching (FastAPI + React)
CvScope is a full-stack web app that compares a candidate resume (PDF/DOCX) against a job description and returns:

Match percentage (TF‑IDF + cosine similarity)
Extracted resume skills and job skills
Matched skills and missing skills
Features
Upload resume (PDF / DOCX)
Paste job description
Skill extraction (regex + simple heuristics)
Skill matching (fuzzy match)
Match percentage (TF‑IDF + cosine similarity)
React UI to display results
Tech Stack
Backend

FastAPI (API server): main.py
PDF parsing: pdfplumber
DOCX parsing: python-docx
Similarity: scikit-learn (TF‑IDF + cosine similarity)
Upload handling: python-multipart (required by FastAPI for form/file uploads)
Frontend

React (Create React App): package.json
Project Structure
Backend
FastAPI — API server
pdfplumber — PDF parsing
python-docx — DOCX parsing
scikit-learn — TF-IDF + cosine similarity
python-multipart — file uploads

Frontend
React (Create React App)
📁 Project Structure
CVScope/
│
├── backend/
│   ├── main.py          # FastAPI app & routes
│   ├── utils.py         # Core logic (NLP, matching, similarity)
│   ├── skill_db.py      # Skill aliases (optional)
│   └── Resume.csv       # Sample data
│
├── frontend/
│   ├── UploadForm.js    # Resume + JD upload
│   ├── ResultCard.js    # Results UI
│   └── package.json
⚙️ Setup & Run (Windows)

⚠️ You must run both backend and frontend simultaneously.

🔹 1. Backend Setup (FastAPI)
Step 1: Create & activate virtual environment
python -m venv .venv
.venv\Scripts\activate

If blocked:

Set-ExecutionPolicy -Scope Process Bypass
Step 2: Install dependencies
python -m pip install --upgrade pip
pip install fastapi uvicorn pdfplumber python-docx scikit-learn python-multipart
Step 3: Run server
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
Step 4: Verify

Open:

http://127.0.0.1:8000/

Expected response:

{"message":"SkillSync Backend Running"}
Important note about the common “uvicorn not recognized” error:

If you run uvicorn main:app --reload and get “uvicorn is not recognized”, use python -m uvicorn ... as shown above. That ensures you’re using the uvicorn installed in your currently activated venv.
2) Start the frontend (React)
Open a second terminal and run:

Open:

http://localhost:3000/
🔗 API Endpoints
✅ Health Check
GET /
📊 Analyze Resume
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
Skill extraction is currently rule-based (regex + heuristics) in utils.py
Similarity score is TF‑IDF + cosine similarity (scikit-learn)
Fuzzy matching uses SequenceMatcher for “close enough” skill matches