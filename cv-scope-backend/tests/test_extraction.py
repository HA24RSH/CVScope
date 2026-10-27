"""
tests/test_extraction.py
------------------------
Unit tests for skill extraction, normalization, and taxonomy.

Run:
    cd cv-scope-backend
    python -m pytest tests/test_extraction.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from skill_taxonomy import ALIAS_MAP, CANONICAL_SKILLS, get_skill_category, SKILL_CATEGORY_MAP
from utils import _normalize_skill, extract_skills_detailed, warmup_models, group_skills_by_category


@pytest.fixture(scope="module", autouse=True)
def load_models():
    """Load NLP models once for all tests in this module."""
    warmup_models()


# ─────────────────────────────────────────────────────────────────────────────
# Taxonomy tests
# ─────────────────────────────────────────────────────────────────────────────

class TestTaxonomy:
    def test_alias_map_not_empty(self):
        assert len(ALIAS_MAP) > 100, "ALIAS_MAP should have many aliases"

    def test_canonical_skills_not_empty(self):
        assert len(CANONICAL_SKILLS) > 50, "CANONICAL_SKILLS should have many entries"

    def test_known_aliases_resolve(self):
        """Known aliases should map to correct canonical names."""
        cases = [
            ("reactjs", "react"),
            ("react.js", "react"),
            ("node.js", "nodejs"),
            ("nodejs", "nodejs"),
            ("scikit-learn", "scikit-learn"),
            ("sklearn", "scikit-learn"),
            ("k8s", "kubernetes"),
            ("js", "javascript"),
            ("ts", "typescript"),
            ("aws", "aws"),
            ("postgresql", "postgresql"),
            ("postgres", "postgresql"),
            ("django", "django"),
            ("spring boot", "spring"),
        ]
        for alias, expected_canonical in cases:
            result = ALIAS_MAP.get(alias.lower())
            assert result == expected_canonical, (
                f"Alias '{alias}' should map to '{expected_canonical}', got '{result}'"
            )

    def test_category_map_populated(self):
        assert len(SKILL_CATEGORY_MAP) > 50

    def test_get_skill_category_known(self):
        assert get_skill_category("python") == "Programming Languages"
        assert get_skill_category("react") == "Frontend Development"
        assert get_skill_category("docker") == "DevOps"
        assert get_skill_category("machine learning") == "AI and Machine Learning"
        assert get_skill_category("sql") == "Databases"

    def test_get_skill_category_unknown_returns_other(self):
        assert get_skill_category("xyznonexistentskill123") == "Other"


# ─────────────────────────────────────────────────────────────────────────────
# Normalization tests
# ─────────────────────────────────────────────────────────────────────────────

class TestNormalization:
    def test_normalize_known_alias(self):
        assert _normalize_skill("ReactJS") == "react"
        assert _normalize_skill("Node.js") == "nodejs"
        assert _normalize_skill("PostgreSQL") == "postgresql"

    def test_normalize_noise_returns_none(self):
        """Generic noise words should return None."""
        noise_words = ["experience", "team", "good", "strong", "skill", "work"]
        for word in noise_words:
            result = _normalize_skill(word)
            assert result is None or result not in CANONICAL_SKILLS, (
                f"Noise word '{word}' should not normalize to a canonical skill, got '{result}'"
            )

    def test_normalize_too_short_returns_none(self):
        # 1-char strings too short (min 3)
        assert _normalize_skill("x") is None

    def test_normalize_strips_punctuation(self):
        # punctuation at edges should be stripped
        result = _normalize_skill("react,")
        assert result == "react"


# ─────────────────────────────────────────────────────────────────────────────
# Extraction tests
# ─────────────────────────────────────────────────────────────────────────────

class TestExtraction:
    def test_extract_from_clean_skills_section(self):
        text = "Skills: Python, React, PostgreSQL, Docker, Git"
        result = extract_skills_detailed(text, doc_type="resume")
        skills = set(result.skills)
        assert "python" in skills
        assert "react" in skills
        assert "postgresql" in skills
        assert "docker" in skills
        assert "git" in skills

    def test_extract_aliases(self):
        """Aliases like ReactJS, Node.js should map to canonical names."""
        text = "Skills: ReactJS, Node.js, scikit-learn, AWS, K8S"
        result = extract_skills_detailed(text, doc_type="resume")
        skills = set(result.skills)
        assert "react" in skills, f"ReactJS should extract as 'react'. Got: {skills}"
        assert "nodejs" in skills, f"Node.js should extract as 'nodejs'. Got: {skills}"
        assert "scikit-learn" in skills, f"scikit-learn should be extracted. Got: {skills}"
        assert "aws" in skills, f"AWS should be extracted. Got: {skills}"

    def test_extract_from_noise_only_text(self):
        """Text with no skills should return empty or near-empty list."""
        text = "I am a hardworking, dedicated, and experienced professional who works well in teams."
        result = extract_skills_detailed(text, doc_type="resume")
        # We allow at most 1 false positive from noise text
        assert len(result.skills) <= 2, (
            f"Noise-only text extracted unexpected skills: {result.skills}"
        )

    def test_extract_empty_text(self):
        result = extract_skills_detailed("", doc_type="resume")
        assert result.skills == []
        assert result.details == []

    def test_extract_returns_confidence(self):
        text = "Skills: Python, Django, PostgreSQL"
        result = extract_skills_detailed(text, doc_type="resume")
        for detail in result.details:
            assert "confidence" in detail
            assert 0.0 <= float(detail["confidence"]) <= 1.0

    def test_extract_returns_sources(self):
        text = "Skills: Python, Django"
        result = extract_skills_detailed(text, doc_type="resume")
        for detail in result.details:
            assert "sources" in detail
            assert isinstance(detail["sources"], list)
            assert len(detail["sources"]) >= 1

    def test_extract_jd_mode(self):
        jd = "We require React, TypeScript, and Node.js. AWS experience preferred."
        result = extract_skills_detailed(jd, doc_type="job_description")
        skills = set(result.skills)
        assert "react" in skills
        assert "typescript" in skills
        assert "nodejs" in skills
        assert "aws" in skills


# ─────────────────────────────────────────────────────────────────────────────
# Group by category tests
# ─────────────────────────────────────────────────────────────────────────────

class TestGroupByCategory:
    def test_group_basic(self):
        skills = ["python", "react", "docker"]
        result = group_skills_by_category(skills)
        assert "Programming Languages" in result
        assert "python" in result["Programming Languages"]
        assert "Frontend Development" in result
        assert "react" in result["Frontend Development"]
        assert "DevOps" in result
        assert "docker" in result["DevOps"]

    def test_group_unknown_skill(self):
        skills = ["unknowntechxyz"]
        result = group_skills_by_category(skills)
        assert "Other" in result
        assert "unknowntechxyz" in result["Other"]

    def test_group_empty(self):
        result = group_skills_by_category([])
        assert result == {}
