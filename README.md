# 🚀 CvScope – Resume Analysis & Skill Matching System

CvScope is a full-stack web application that analyzes a candidate’s resume against a job description (JD) and provides intelligent insights such as match percentage, skill comparison, and learning recommendations.

---

## 🧠 Features

- 📄 Upload Resume (PDF / DOCX)
- 📝 Paste Job Description
- 🔍 Automatic Skill Extraction (Dynamic – No fixed list)
- 📊 Match Percentage using ML (TF-IDF + Cosine Similarity)
- ✅ Matched Skills
- ❌ Missing Skills
- 📚 Learning Recommendations for Missing Skills
- 💻 Clean and responsive React UI

---

## 🏗️ Tech Stack

### Frontend
- React (Create React App)
- CSS

### Backend
- FastAPI (Python)
- spaCy (NLP)
- scikit-learn (Machine Learning)
- pdfplumber (PDF parsing)
- python-docx (DOCX parsing)

---

## 📁 Project Structure
    cvscope/
    │
    ├── backend/
    │ ├── main.py
    │ ├── utils.py
    │ ├── recommender.py
    │ ├── skill_db.py (optional)
    │ ├── requirements.txt
    │
    ├── cv-scope-frontend/
    │ ├── src/
    │ │ ├── components/
    │ │ ├── App.js
    │ │ ├── index.js
    │ │ └── styles/
    │ ├── package.json
    │
    └── README.md

---

## ⚙️ Installation & Setup

### 🔹 1. Clone the Repository

```bash
git clone https://github.com/your-username/cvscope.git
cd cvscope

---

    Backend Setup (FastAPI) :

    📌 Step 1: Navigate to backend
        cd backend

    📌 Step 2: Create Virtual Environment
        python -m venv venv

    📌 Step 3: Activate Virtual Environment
        Windows:
            venv\Scripts\activate
        Mac/Linux:
            source venv/bin/activate

    📌 Step 4: Install Dependencies
        pip install -r requirements.txt

    If requirements.txt is missing, install manually:

    pip install fastapi uvicorn pdfplumber python-docx spacy scikit-learn

    📌 Step 5: Install spaCy Model
        python -m spacy download en_core_web_sm

    📌 Step 6: Run Backend Server
        uvicorn main:app --reload

👉 Backend will run at:

http://127.0.0.1:8000

---

    🌐 Frontend Setup (React)
    📌 Step 1: Navigate to frontend
        cd cv-scope-frontend

    📌 Step 2: Install dependencies
        npm install

    📌 Step 3: Run frontend
        npm start

👉 Frontend will run at:

http://localhost:3000