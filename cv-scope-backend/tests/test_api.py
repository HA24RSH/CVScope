"""
tests/test_api.py
-----------------
Integration tests for the CVScope FastAPI /analyze endpoint.

Requires httpx (used by FastAPI's TestClient) and a valid PDF/DOCX fixture.
Since we can't ship a real PDF in tests, we build a minimal one-page PDF in-memory
using pdfplumber's dependency (pdfminer) or a raw PDF byte-stream.

Run:
    cd cv-scope-backend
    python -m pytest tests/test_api.py -v
"""

import io
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from main import app


# ─────────────────────────────────────────────────────────────────────────────
# Helpers — build a minimal valid PDF in-memory
# ─────────────────────────────────────────────────────────────────────────────

def _make_minimal_pdf(text: str) -> bytes:
    """
    Build a minimal, valid single-page PDF that contains the given text.
    Uses only the standard library — no reportlab/fpdf required.

    The PDF embeds the text inside a BT (Begin Text) / ET (End Text) block
    using the Helvetica base font (always available, no font embedding needed).

    This is sufficient for pdfplumber to extract the text back out.
    """
    # Escape special PDF chars
    safe = (
        text
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )

    # Build objects
    objects: list[bytes] = []

    def _add(content: str) -> int:
        objects.append(content.encode("latin-1"))
        return len(objects)  # 1-indexed object number

    # 1  — Catalog
    cat_n = _add("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

    # 2  — Pages
    pages_n = _add("2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")

    # 3  — Page
    page_n = _add(
        "3 0 obj\n"
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]\n"
        "   /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\n"
        "endobj\n"
    )

    # 4  — Content stream
    stream_body = f"BT\n/F1 12 Tf\n50 700 Td\n({safe}) Tj\nET\n"
    stream_n = _add(
        f"4 0 obj\n<< /Length {len(stream_body)} >>\nstream\n{stream_body}endstream\nendobj\n"
    )

    # 5  — Font
    font_n = _add(
        "5 0 obj\n"
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\n"
        "endobj\n"
    )

    # Assemble xref table
    header = b"%PDF-1.4\n"
    body = b"".join(objects)
    xref_pos = len(header) + len(body)

    # Compute byte offsets for each object
    offsets: list[int] = []
    pos = len(header)
    for obj_bytes in objects:
        offsets.append(pos)
        pos += len(obj_bytes)

    n = len(objects)
    xref_lines = [f"xref\n0 {n + 1}\n0000000000 65535 f \n"]
    for off in offsets:
        xref_lines.append(f"{off:010d} 00000 n \n")
    xref = "".join(xref_lines).encode("latin-1")

    trailer = (
        f"trailer\n<< /Size {n + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos + len(xref)}\n%%EOF\n"
    ).encode("latin-1")

    # NOTE: xref_pos should point to start of xref, not xref+xref
    # Recalculate correctly
    xref_start = len(header) + len(body)
    xref = "".join(xref_lines).encode("latin-1")
    trailer = (
        f"trailer\n<< /Size {n + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_start}\n%%EOF\n"
    ).encode("latin-1")

    return header + body + xref + trailer


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

SAMPLE_RESUME_TEXT = (
    "Skills: Python, Django, PostgreSQL, Docker, Git, REST API, AWS\n"
    "Experience: 3 years building backend services with Python and Django.\n"
    "Education: B.Sc. Computer Science."
)

SAMPLE_JD = (
    "We are looking for a Backend Engineer with strong Python and Django skills. "
    "Experience with PostgreSQL, Docker, and REST API design is required. "
    "AWS or GCP cloud experience is a plus. "
    "Familiarity with CI/CD pipelines is preferred."
)


@pytest.fixture(scope="module")
def client():
    """Shared test client — models are loaded once via lifespan."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def sample_pdf_bytes():
    return _make_minimal_pdf(SAMPLE_RESUME_TEXT)


# ─────────────────────────────────────────────────────────────────────────────
# Health check tests
# ─────────────────────────────────────────────────────────────────────────────

class TestHealthEndpoints:
    def test_root_returns_200(self, client):
        res = client.get("/")
        assert res.status_code == 200
        data = res.json()
        assert data.get("status") == "ok"

    def test_health_returns_ok(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json().get("status") == "ok"


# ─────────────────────────────────────────────────────────────────────────────
# /analyze — validation tests (no NLP required for most of these)
# ─────────────────────────────────────────────────────────────────────────────

class TestAnalyzeValidation:
    def test_missing_file_returns_422(self, client):
        """No file at all → 422 Unprocessable Entity."""
        res = client.post("/analyze", data={"job_description": SAMPLE_JD})
        assert res.status_code == 422

    def test_missing_jd_returns_422(self, client, sample_pdf_bytes):
        """No job_description field → 422."""
        res = client.post(
            "/analyze",
            files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
        )
        assert res.status_code == 422

    def test_unsupported_file_type_returns_400(self, client):
        """Uploading a .txt file → 400 Bad Request."""
        res = client.post(
            "/analyze",
            files={"resume": ("resume.txt", b"some text", "text/plain")},
            data={"job_description": SAMPLE_JD},
        )
        assert res.status_code == 400
        assert "txt" in res.json().get("detail", "").lower() or "unsupported" in res.json().get("detail", "").lower()

    def test_short_jd_returns_400(self, client, sample_pdf_bytes):
        """JD shorter than 30 chars → 400."""
        res = client.post(
            "/analyze",
            files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
            data={"job_description": "Too short"},
        )
        assert res.status_code in (400, 422)

    def test_empty_jd_returns_400(self, client, sample_pdf_bytes):
        """Empty JD → 400."""
        res = client.post(
            "/analyze",
            files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
            data={"job_description": ""},
        )
        assert res.status_code in (400, 422)


# ─────────────────────────────────────────────────────────────────────────────
# /analyze — full integration tests
# ─────────────────────────────────────────────────────────────────────────────

class TestAnalyzeSuccess:
    """
    These tests send a real request through the full NLP pipeline.
    They rely on the spaCy model being available (en_core_web_sm).
    """

    def test_returns_200_with_valid_inputs(self, client, sample_pdf_bytes):
        res = client.post(
            "/analyze",
            files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
            data={"job_description": SAMPLE_JD},
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"

    def test_response_has_required_fields(self, client, sample_pdf_bytes):
        res = client.post(
            "/analyze",
            files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
            data={"job_description": SAMPLE_JD},
        )
        assert res.status_code == 200
        data = res.json()
        required_fields = [
            "match_percentage",
            "resume_skills",
            "job_skills",
            "matched_skills",
            "missing_skills",
            "similarity_breakdown",
            "resume_skill_details",
            "job_skill_details",
            "skill_categories",
            "score_explanation",
            "skill_recommendations",
            "role_matches",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: '{field}'"

    def test_match_percentage_in_range(self, client, sample_pdf_bytes):
        res = client.post(
            "/analyze",
            files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
            data={"job_description": SAMPLE_JD},
        )
        assert res.status_code == 200
        pct = res.json().get("match_percentage", -1)
        assert 0.0 <= pct <= 100.0, f"match_percentage out of range: {pct}"

    def test_matched_plus_missing_equals_jd_skills(self, client, sample_pdf_bytes):
        """matched + missing must cover every JD skill exactly once."""
        res = client.post(
            "/analyze",
            files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
            data={"job_description": SAMPLE_JD},
        )
        assert res.status_code == 200
        data = res.json()
        jd_skills = set(data.get("job_skills", []))
        matched = set(data.get("matched_skills", []))
        missing = set(data.get("missing_skills", []))
        # Every JD skill should appear in exactly one of matched / missing
        assert matched | missing == jd_skills, (
            f"matched ∪ missing ≠ jd_skills.\n"
            f"  jd_skills = {sorted(jd_skills)}\n"
            f"  matched   = {sorted(matched)}\n"
            f"  missing   = {sorted(missing)}"
        )
        assert matched & missing == set(), "A skill cannot be both matched and missing"

    def test_resume_skills_list_is_non_empty(self, client, sample_pdf_bytes):
        """A resume with explicit skill keywords must extract at least some skills."""
        res = client.post(
            "/analyze",
            files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
            data={"job_description": SAMPLE_JD},
        )
        assert res.status_code == 200
        data = res.json()
        assert len(data.get("resume_skills", [])) > 0, "No skills extracted from a clearly skill-rich resume"

    def test_similarity_breakdown_keys(self, client, sample_pdf_bytes):
        res = client.post(
            "/analyze",
            files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
            data={"job_description": SAMPLE_JD},
        )
        assert res.status_code == 200
        bd = res.json().get("similarity_breakdown", {})
        assert "skill_match_score" in bd
        assert "text_similarity_score" in bd
        assert "final_score" in bd
        assert "formula" in bd

    def test_score_explanation_is_non_empty_list(self, client, sample_pdf_bytes):
        res = client.post(
            "/analyze",
            files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
            data={"job_description": SAMPLE_JD},
        )
        assert res.status_code == 200
        explanation = res.json().get("score_explanation", [])
        assert isinstance(explanation, list)
        assert len(explanation) >= 1

    def test_role_matches_is_list(self, client, sample_pdf_bytes):
        res = client.post(
            "/analyze",
            files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
            data={"job_description": SAMPLE_JD},
        )
        assert res.status_code == 200
        roles = res.json().get("role_matches", [])
        assert isinstance(roles, list)
        if roles:
            first = roles[0]
            assert "role" in first
            assert "overall_score" in first
            assert 0.0 <= first["overall_score"] <= 100.0

    def test_skill_recommendations_structure(self, client, sample_pdf_bytes):
        res = client.post(
            "/analyze",
            files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
            data={"job_description": SAMPLE_JD},
        )
        assert res.status_code == 200
        recs = res.json().get("skill_recommendations", [])
        assert isinstance(recs, list)
        for rec in recs:
            assert "skill" in rec
            assert "why_it_matters" in rec
            assert "learning_order" in rec
            assert "has_detailed_guide" in rec

    def test_response_is_json_serializable(self, client, sample_pdf_bytes):
        """Verify no numpy types or other non-serializable objects leaked into the response."""
        import json
        res = client.post(
            "/analyze",
            files={"resume": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
            data={"job_description": SAMPLE_JD},
        )
        assert res.status_code == 200
        # If we got here, FastAPI serialized it — just double-check the raw text parses
        parsed = json.loads(res.text)
        assert isinstance(parsed, dict)
