# CVScope — AI-Powered Resume Analyzer

> **100% local. No cloud APIs. No data leaves your machine.**

CVScope is a full-stack NLP application that scores how well a resume matches a job description, extracts skills with explainability, identifies skill gaps, generates learning recommendations, and matches the candidate's profile to predefined job roles.

---

## Features

| Feature | Detail |
|---|---|
| **4-layer skill extraction** | PhraseMatcher → NER → Noun-chunks → YAKE keyphrase |
| **Section-aware parsing** | Skills section gets highest weight; experience/education get lower |
| **Confidence scoring** | Per-skill confidence: `base_confidence × section_weight × techiness_multiplier` |
| **Fuzzy matching** | RapidFuzz `token_sort_ratio ≥ 85` for alias tolerance |
| **TF-IDF similarity** | Section-weighted cosine similarity: 50% skills + 30% experience + 20% full doc |
| **Skill gap analysis** | Learning paths, prerequisites, practice projects for every missing skill |
| **Job role matching** | Score against 12 predefined role profiles (70% required + 30% preferred) |
| **Explainability** | Plain-English score narrative + full formula breakdown in UI |
| **Skill categorisation** | 13 categories: Languages, Frontend, Backend, Databases, AI/ML, DevOps… |
| **220+ skills** | Curated taxonomy with hundreds of aliases (ReactJS → react, k8s → kubernetes) |

---

## Project Structure

```
CVScope/
├── cv-scope-backend/
│   ├── main.py                    # FastAPI app (POST /analyze, GET /health)
│   ├── utils.py                   # 4-layer NLP pipeline + scoring
│   ├── skill_taxonomy.py          # 220+ skills, alias map, categories
│   ├── recommendations.py         # Skill gap + role matching logic
│   ├── skill_recommendations.json # Learning paths per skill
│   ├── job_roles.json             # 12 role profiles
│   ├── evaluate.py                # Local P/R/F1 evaluation script
│   ├── requirements.txt           # Python dependencies
│   └── tests/
│       ├── test_extraction.py     # Taxonomy, normalization, extraction tests
│       ├── test_matching.py       # Matching + scoring formula tests
│       ├── test_recommendations.py# Skill gap + role matching tests
│       ├── test_api.py            # Full API integration tests
│       └── evaluation_dataset.json# Synthetic test dataset
│
└── cv-scope-frontend/
    ├── src/
    │   ├── App.js                 # Root — wires UploadForm → Dashboard
    │   ├── components/
    │   │   ├── Header.js
    │   │   ├── UploadForm.js      # File upload + JD textarea + analyze button
    │   │   ├── Dashboard.js       # Tab router (5 tabs)
    │   │   ├── ScoreOverview.js   # Gauge + metric bars + skill pills
    │   │   ├── SkillsPanel.js     # By-category / resume / JD views
    │   │   ├── RecommendationsPanel.js  # Skill gap cards with learning paths
    │   │   ├── RolesPanel.js      # Job role match bars
    │   │   └── ExplainPanel.js    # Score narrative + AI concepts
    │   └── styles/global.css      # Dark glassmorphism design system
    └── package.json
```

---

## Quick Start

### Backend

```bash
cd cv-scope-backend

# 1. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download the spaCy model (required)
python -m spacy download en_core_web_sm

# 4. Start the server
uvicorn main:app --reload
# → http://127.0.0.1:8000
```

### Frontend

```bash
cd cv-scope-frontend

npm install
npm start
# → http://localhost:3000
```

---

## API Reference

### `GET /`
Health check. Returns `{"message": "CVScope Backend v3 Running", "status": "ok"}`.

### `GET /health`
Lightweight ping. Returns `{"status": "ok"}`.

### `POST /analyze`

**Request:** `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `resume` | File | PDF or DOCX (max 10 MB) |
| `job_description` | string | Raw job description text (min 30 chars) |

**Response:** JSON object

| Field | Type | Description |
|---|---|---|
| `match_percentage` | float | Final weighted score 0–100 |
| `resume_skills` | list[str] | Canonical skills from resume |
| `job_skills` | list[str] | Canonical skills from JD |
| `matched_skills` | list[str] | JD skills found in resume |
| `missing_skills` | list[str] | JD skills NOT in resume |
| `similarity_breakdown` | dict | Component scores + formula string |
| `resume_skill_details` | list[dict] | Per-skill confidence + sources + sections |
| `job_skill_details` | list[dict] | Same, for JD |
| `skill_categories` | dict | Resume skills grouped by category |
| `score_explanation` | list[str] | Plain-English explanation of the score |
| `skill_recommendations` | list[dict] | Learning paths for missing skills |
| `role_matches` | list[dict] | Top 5 job role matches with coverage breakdown |

---

## Scoring Formula

```
final_score = 0.60 × skill_match_score + 0.40 × text_similarity_score

skill_match_score  = confidence-weighted JD skill coverage × 100
text_similarity    = section-weighted TF-IDF cosine similarity × 100
                     (50% skills section + 30% experience + 20% full doc)
```

---

## Running Tests

```bash
cd cv-scope-backend

# All tests
python -m pytest tests/ -v

# Individual suites
python -m pytest tests/test_extraction.py -v
python -m pytest tests/test_matching.py -v
python -m pytest tests/test_recommendations.py -v
python -m pytest tests/test_api.py -v
```

## Running Evaluation

```bash
cd cv-scope-backend
python evaluate.py
```

Reports per-test and aggregate Precision / Recall / F1 for skill extraction, and exact-match accuracy for skill matching.

> ⚠️ The evaluation dataset is **synthetic** (manually created). Results on real-world resumes may differ.

---

## Limitations

1. **Keyword-based only** — The score reflects textual overlap, not professional competence.
2. **No semantic embeddings** — Synonyms not in the taxonomy may be missed. The alias map and fuzzy matching partially address this.
3. **Image-based PDFs** — Scanned PDFs without embedded text cannot be processed.
4. **Evaluation dataset size** — 10 extraction tests are too small for reliable generalisation.
5. **Role profiles are static** — The 12 job role profiles were manually curated and may not reflect all job markets.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, FastAPI, Uvicorn |
| NLP | spaCy (`en_core_web_sm`), YAKE |
| Matching | RapidFuzz |
| Similarity | scikit-learn TF-IDF + cosine similarity |
| PDF parsing | pdfplumber |
| DOCX parsing | python-docx |
| Frontend | React 19, vanilla CSS, glassmorphism dark theme |
| Testing | pytest, httpx (FastAPI TestClient) |