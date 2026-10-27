"""
tests/test_matching.py
----------------------
Unit tests for skill matching and similarity scoring.

Run:
    cd cv-scope-backend
    python -m pytest tests/test_matching.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from utils import match_skills, calculate_similarity, warmup_models


@pytest.fixture(scope="module", autouse=True)
def load_models():
    warmup_models()


# ─────────────────────────────────────────────────────────────────────────────
# match_skills tests
# ─────────────────────────────────────────────────────────────────────────────

class TestMatchSkills:
    def test_exact_match_all(self):
        resume = ["python", "react", "docker"]
        jd = ["python", "react", "docker"]
        result = match_skills(resume, jd)
        assert set(result.matched) == {"python", "react", "docker"}
        assert result.missing == []

    def test_exact_match_partial(self):
        resume = ["python", "django"]
        jd = ["python", "react", "django", "typescript"]
        result = match_skills(resume, jd)
        assert "python" in result.matched
        assert "django" in result.matched
        assert "react" in result.missing
        assert "typescript" in result.missing

    def test_no_match(self):
        resume = ["python"]
        jd = ["react", "docker", "typescript"]
        result = match_skills(resume, jd)
        assert result.matched == []
        assert set(result.missing) == {"react", "docker", "typescript"}

    def test_empty_jd(self):
        result = match_skills(["python"], [])
        assert result.matched == []
        assert result.missing == []

    def test_empty_resume(self):
        result = match_skills([], ["python", "react"])
        assert result.matched == []
        assert set(result.missing) == {"python", "react"}

    def test_both_empty(self):
        result = match_skills([], [])
        assert result.matched == []
        assert result.missing == []

    def test_fuzzy_match_reactjs(self):
        """reactjs should fuzzy-match to react in JD."""
        resume = ["reactjs"]
        jd = ["react"]
        result = match_skills(resume, jd)
        # react should be matched (fuzzy)
        assert "react" in result.matched or len(result.matched) == 1

    def test_no_duplicate_in_matched(self):
        """Skills should not appear multiple times in matched list."""
        resume = ["python", "python", "django"]
        jd = ["python", "django"]
        result = match_skills(resume, jd)
        assert result.matched.count("python") == 1
        assert result.matched.count("django") == 1

    def test_ordering(self):
        """matched + missing should cover all JD skills."""
        resume = ["python", "react"]
        jd = ["python", "react", "docker", "typescript"]
        result = match_skills(resume, jd)
        all_skills = set(result.matched) | set(result.missing)
        assert all_skills == set(jd)


# ─────────────────────────────────────────────────────────────────────────────
# calculate_similarity tests
# ─────────────────────────────────────────────────────────────────────────────

class TestCalculateSimilarity:
    def test_returns_required_keys(self):
        breakdown = calculate_similarity(
            resume_skills=["python", "django"],
            jd_skills=["python", "django"],
            resume_text="Python developer with Django experience.",
            jd_text="We need a Python Django developer.",
        )
        assert "skill_match_score" in breakdown
        assert "text_similarity_score" in breakdown
        assert "final_score" in breakdown
        assert "formula" in breakdown

    def test_score_range(self):
        breakdown = calculate_similarity(
            resume_skills=["python", "react"],
            jd_skills=["python", "react", "typescript"],
            resume_text="Python and React developer.",
            jd_text="Python React TypeScript developer needed.",
        )
        assert 0.0 <= breakdown["skill_match_score"] <= 100.0
        assert 0.0 <= breakdown["text_similarity_score"] <= 100.0
        assert 0.0 <= breakdown["final_score"] <= 100.0

    def test_empty_jd_skills(self):
        breakdown = calculate_similarity(
            resume_skills=["python"],
            jd_skills=[],
            resume_text="Python developer",
            jd_text="Looking for someone",
        )
        assert breakdown["skill_match_score"] == 0.0
        assert breakdown["final_score"] == 0.0

    def test_perfect_match_boosts_score(self):
        """When resume perfectly matches JD, score should be high."""
        skills = ["python", "django", "postgresql", "docker", "git"]
        breakdown_perfect = calculate_similarity(
            resume_skills=skills,
            jd_skills=skills,
            resume_text="Python Django PostgreSQL Docker Git developer.",
            jd_text="Need Python Django PostgreSQL Docker Git developer.",
        )
        breakdown_empty = calculate_similarity(
            resume_skills=[],
            jd_skills=skills,
            resume_text="I am a developer.",
            jd_text="Need Python Django PostgreSQL Docker Git developer.",
        )
        assert breakdown_perfect["final_score"] > breakdown_empty["final_score"]

    def test_scores_are_python_float(self):
        """Scores must be JSON-serialisable Python floats, not numpy types."""
        import json
        breakdown = calculate_similarity(
            resume_skills=["python"],
            jd_skills=["python", "react"],
            resume_text="Python developer",
            jd_text="Python and React",
        )
        # This will raise if any value is numpy.float64
        json.dumps(breakdown)

    def test_formula_string_present(self):
        breakdown = calculate_similarity(
            resume_skills=["python"],
            jd_skills=["python"],
        )
        assert isinstance(breakdown.get("formula"), str)
        assert len(breakdown["formula"]) > 20


# ─────────────────────────────────────────────────────────────────────────────
# Scoring formula validation
# ─────────────────────────────────────────────────────────────────────────────

class TestScoringFormula:
    def test_formula_weights(self):
        """Verify the 60/40 weighting is applied correctly."""
        # Set up a case where we can predict the score
        resume = ["python", "react"]
        jd = ["python", "react", "typescript"]  # 2/3 match = 66.67% skill match

        breakdown = calculate_similarity(
            resume_skills=resume,
            jd_skills=jd,
            resume_text="",  # skip text similarity
            jd_text="",
        )
        skill_score = breakdown["skill_match_score"]
        text_score = breakdown["text_similarity_score"]
        expected_final = round(0.6 * skill_score + 0.4 * text_score, 2)
        assert abs(breakdown["final_score"] - expected_final) < 0.01, (
            f"Formula mismatch: 0.6×{skill_score} + 0.4×{text_score} ≠ {breakdown['final_score']}"
        )
