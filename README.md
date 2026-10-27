# CVScope

CVScope is a local, full-stack resume analyzer. It compares a PDF or DOCX
resume with a job description and provides:

- Resume and job-description skill extraction
- Alias-aware and fuzzy skill matching
- Confidence scores and extraction evidence
- Section-weighted TF-IDF similarity
- Skill categories and missing-skill analysis
- Offline learning recommendations
- Matching against predefined job roles
- Plain-English score explanations

No resume or job-description data is sent to a cloud API. The backend runs
locally on your machine.

## Requirements

- Windows, macOS, or Linux
- Python 3.10 or newer
- Node.js 18 or newer
- npm
- At least 2 GB of free disk space for Python and Node dependencies

The backend uses the spaCy `en_core_web_sm` language model. It must be
downloaded once after installing the Python packages.

## Project structure

```text
CVScope/
├── cv-scope-backend/
│   ├── main.py
│   ├── utils.py
│   ├── skill_taxonomy.py
│   ├── recommendations.py
│   ├── skill_recommendations.json
│   ├── job_roles.json
│   ├── evaluate.py
│   ├── requirements.txt
│   └── tests/
└── cv-scope-frontend/
    ├── src/
    ├── public/
    ├── package.json
    └── .env.example
```

## Installation on Windows

Open PowerShell in the repository root:

```powershell
cd "G:\web projects\CVScope"
```

### 1. Install and configure the backend

```powershell
cd .\cv-scope-backend

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

If PowerShell prevents virtual-environment activation, run this once in the
same terminal and retry:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 2. Install the frontend

Open a second PowerShell terminal:

```powershell
cd "G:\web projects\CVScope\cv-scope-frontend"
npm install
```

The frontend already defaults to `http://127.0.0.1:8000`. To configure the
backend URL explicitly:

```powershell
Copy-Item .env.example .env.local
```

Edit `.env.local` if necessary:

```env
REACT_APP_API_BASE_URL=http://127.0.0.1:8000
```

Restart the frontend after changing environment variables.

## Run the application

Use two terminals.

### Terminal 1: backend

```powershell
cd "G:\web projects\CVScope\cv-scope-backend"
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

Backend URLs:

- API: http://127.0.0.1:8000
- Swagger API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

### Terminal 2: frontend

```powershell
cd "G:\web projects\CVScope\cv-scope-frontend"
npm start
```

Open http://localhost:3000 in a browser.

Upload a PDF or DOCX resume, paste a job description with at least 30
characters, and click **Analyze Match**.

## Run on macOS or Linux

### Backend

```bash
cd cv-scope-backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --reload
```

### Frontend

In a second terminal:

```bash
cd cv-scope-frontend
npm install
npm start
```

Open http://localhost:3000.

## Test the backend

Activate the backend virtual environment, then run:

```powershell
cd "G:\web projects\CVScope\cv-scope-backend"
.\.venv\Scripts\Activate.ps1
python -m pytest tests -v
```

The test suite covers:

- Taxonomy and alias normalization
- Multi-layer skill extraction
- Skill matching and scoring
- Recommendations and role matching
- FastAPI validation and full `/analyze` integration

## Run the evaluation script

```powershell
cd "G:\web projects\CVScope\cv-scope-backend"
.\.venv\Scripts\Activate.ps1
python evaluate.py
```

The evaluation uses the synthetic dataset at
`cv-scope-backend/tests/evaluation_dataset.json`. Its metrics are useful for
regression testing, but they are not a benchmark for real-world resumes.

## Build the frontend

```powershell
cd "G:\web projects\CVScope\cv-scope-frontend"
npm run build
```

The optimized static files are created in `cv-scope-frontend/build`.

## API overview

### `GET /`

Returns the backend status.

### `GET /health`

Returns:

```json
{"status": "ok"}
```

### `POST /analyze`

Send a `multipart/form-data` request with:

| Field | Type | Required | Description |
|---|---|---:|---|
| `resume` | file | Yes | PDF or DOCX file, maximum 10 MB |
| `job_description` | string | Yes | Job description, minimum 30 characters |

The response includes the final match percentage, extracted skills, matched
and missing skills, score components, confidence details, categories, learning
recommendations, and role matches.

You can try the endpoint interactively at
http://127.0.0.1:8000/docs.

## Scoring

```text
final_score = 0.60 * skill_match_score
            + 0.40 * text_similarity_score
```

The text similarity score uses section-aware TF-IDF weighting. Skills,
experience, and the complete document contribute different weights.

## Troubleshooting

### `No module named ...`

Make sure the backend virtual environment is active:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### spaCy model not found

Run:

```powershell
python -m spacy download en_core_web_sm
```

### Frontend cannot connect to the backend

Check that:

1. The backend terminal is running `uvicorn`.
2. `http://127.0.0.1:8000/health` returns `{"status":"ok"}`.
3. `REACT_APP_API_BASE_URL` points to the correct backend URL.
4. The frontend was restarted after changing `.env.local`.

### Resume text cannot be extracted

CVScope supports text-based PDF files and DOCX files. Scanned or image-only
PDFs require OCR before they can be analyzed.

## Limitations

- The score measures textual and skill overlap; it does not measure actual
  professional ability.
- Skills outside the local taxonomy may not be detected.
- Static role profiles and learning paths are included locally.
- Scanned PDFs without an embedded text layer are not supported.
- Evaluation data is synthetic and intentionally small.

## Technology stack

- Backend: FastAPI, Uvicorn, Python
- NLP: spaCy, YAKE
- Matching: RapidFuzz
- Similarity: scikit-learn TF-IDF and cosine similarity
- File parsing: pdfplumber and python-docx
- Frontend: React and Create React App
- Testing: pytest and FastAPI TestClient
