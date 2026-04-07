🚀 CvScope — Resume Analysis & Skill Matching System

CvScope is a full-stack web application that analyzes a candidate’s resume against a job description and provides intelligent insights like skill gaps and match percentage.

✨ Features
📄 Upload Resume (PDF / DOCX)
📝 Paste Job Description
🧠 Skill Extraction (regex + heuristics)
🔍 Fuzzy Skill Matching
📊 Match Percentage (TF-IDF + Cosine Similarity)
⚡ FastAPI backend for efficient processing
🎨 React frontend for clean UI visualization
🛠️ Tech Stack

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
🔹 2. Frontend Setup (React)
cd frontend
npm install
npm start

Open:

http://localhost:3000/
🔗 API Endpoints
✅ Health Check
GET /
📊 Analyze Resume
POST /analyze
Content-Type: multipart/form-data
Inputs:
resume → PDF/DOCX file
job_description → text
Response:
{
  "match_percentage": 85,
  "resume_skills": [],
  "job_skills": [],
  "matched_skills": [],
  "missing_skills": []
}
⚡ How It Works
Resume text extracted (PDF/DOCX)
Job description parsed
Skills extracted using heuristics
Fuzzy matching identifies overlaps
TF-IDF + cosine similarity calculates match score
Results displayed in React UI
🐞 Troubleshooting
❌ uvicorn not recognized
python -m uvicorn main:app --reload
❌ multipart/form-data error
pip install python-multipart
❌ Backend not connecting
Check: http://127.0.0.1:8000/
Verify API URL in UploadForm.js
