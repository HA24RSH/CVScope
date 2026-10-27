"""
tests/test_recommendations.py
------------------------------
Unit tests for recommendations module (skill gap + role matching).

Run:
    cd cv-scope-backend
    python -m pytest tests/test_recommendations.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from recommendations import (
    get_skill_gap_recommendations,
    get_role_recommendations,
    generate_score_explanation,
)


class TestSkillGapRecommendations:
    def test_known_skill_returns_guide(self):
        recs = get_skill_gap_recommendations(["python"])
        assert len(recs) == 1
        rec = recs[0]
        assert rec["skill"] == "python"
        assert rec["has_detailed_guide"] is True
        assert isinstance(rec["learning_order"], list)
        assert len(rec["learning_order"]) > 0
        assert isinstance(rec["suggested_project"], str)
        assert len(rec["suggested_project"]) > 10

    def test_unknown_skill_returns_generic(self):
        recs = get_skill_gap_recommendations(["xyznoexisttech999"])
        assert len(recs) == 1
        rec = recs[0]
        assert rec["has_detailed_guide"] is False
        assert len(rec["learning_order"]) > 0  # still has generic guidance

    def test_empty_input(self):
        recs = get_skill_gap_recommendations([])
        assert recs == []

    def test_multiple_skills(self):
        recs = get_skill_gap_recommendations(["react", "docker", "sql"])
        assert len(recs) == 3
        skills_returned = {r["skill"] for r in recs}
        assert "react" in skills_returned
        assert "docker" in skills_returned
        assert "sql" in skills_returned

    def test_resources_are_dicts(self):
        recs = get_skill_gap_recommendations(["python"])
        for resource in recs[0]["resources"]:
            assert "title" in resource
            assert "url" in resource

    def test_prerequisites_are_list(self):
        recs = get_skill_gap_recommendations(["python"])
        assert isinstance(recs[0]["prerequisites"], list)


class TestRoleRecommendations:
    def test_returns_list(self):
        result = get_role_recommendations(["python", "react", "docker"])
        assert isinstance(result, list)

    def test_returns_top_n(self):
        result = get_role_recommendations(["python", "react"], top_n=3)
        assert len(result) <= 3

    def test_result_structure(self):
        result = get_role_recommendations(["python", "django", "postgresql"])
        assert len(result) > 0
        role = result[0]
        required_keys = {"role", "description", "overall_score", "required_coverage",
                         "preferred_coverage", "matched_required", "missing_required",
                         "matched_preferred", "missing_preferred"}
        for key in required_keys:
            assert key in role, f"Missing key: {key}"

    def test_score_range(self):
        result = get_role_recommendations(["python", "react"])
        for role in result:
            assert 0.0 <= role["overall_score"] <= 100.0
            assert 0.0 <= role["required_coverage"] <= 100.0
            assert 0.0 <= role["preferred_coverage"] <= 100.0

    def test_sorted_by_score(self):
        result = get_role_recommendations(["python", "machine learning", "pandas", "numpy", "scikit-learn"])
        scores = [r["overall_score"] for r in result]
        assert scores == sorted(scores, reverse=True), "Results should be sorted by score descending"

    def test_empty_skills(self):
        result = get_role_recommendations([])
        # Should still return roles (all with 0% coverage)
        assert isinstance(result, list)
        for role in result:
            assert role["overall_score"] == 0.0


class TestScoreExplanation:
    def test_basic_explanation(self):
        lines = generate_score_explanation(
            matched_skills=["python", "react"],
            missing_skills=["typescript", "docker"],
            skill_match_score=50.0,
            text_similarity_score=35.0,
            final_score=44.0,
        )
        assert len(lines) >= 3
        # Should mention the match count
        combined = " ".join(lines)
        assert "python" in combined.lower() or "react" in combined.lower() or "2 out of 4" in combined

    def test_formula_explanation_present(self):
        lines = generate_score_explanation(
            matched_skills=["python"],
            missing_skills=["react"],
            skill_match_score=50.0,
            text_similarity_score=30.0,
            final_score=42.0,
        )
        combined = " ".join(lines)
        assert "60%" in combined or "0.60" in combined or "60" in combined

    def test_empty_jd_explanation(self):
        lines = generate_score_explanation(
            matched_skills=[],
            missing_skills=[],
            skill_match_score=0.0,
            text_similarity_score=0.0,
            final_score=0.0,
        )
        assert len(lines) >= 1
        # Should warn about no skills
        combined = " ".join(lines).lower()
        assert "no skills" in combined or "cannot" in combined or "0" in combined

    def test_caveat_present(self):
        lines = generate_score_explanation(
            matched_skills=["python"],
            missing_skills=["react"],
            skill_match_score=50.0,
            text_similarity_score=30.0,
            final_score=42.0,
        )
        combined = " ".join(lines).lower()
        # Should include the disclaimer about not predicting hiring
        assert "not predict" in combined or "does not predict" in combined or "hiring" in combined or "probability" in combined
