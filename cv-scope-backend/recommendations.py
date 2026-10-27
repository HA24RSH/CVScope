"""
recommendations.py  —  CVScope Skill Gap & Role Matching Module
===============================================================
Entirely local, no external API calls.

Features:
  - Skill gap analysis: for each missing skill, provide learning path,
    prerequisites, suggested project, and (when known) reliable resources.
  - Job-role matching: compare resume skills against local role profiles
    and rank roles by skill coverage.

Data sources (local JSON files loaded once at import time):
  - skill_recommendations.json  — learning paths per skill
  - job_roles.json              — role profiles (required + preferred skills)
"""

from __future__ import annotations

import json
import logging
import os
from typing import NamedTuple

from rapidfuzz import fuzz, process

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Load local data files once at module import
# ─────────────────────────────────────────────────────────────────────────────

_DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_json(filename: str) -> dict | list:
    path = os.path.join(_DATA_DIR, filename)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning("Could not load %s: %s", filename, e)
        return {}


_SKILL_REC: dict = _load_json("skill_recommendations.json")   # type: ignore[assignment]
_JOB_ROLES: list = _load_json("job_roles.json")               # type: ignore[assignment]


# ─────────────────────────────────────────────────────────────────────────────
# Skill Gap Analysis
# ─────────────────────────────────────────────────────────────────────────────

class SkillRecommendation(NamedTuple):
    skill: str
    why_it_matters: str
    prerequisites: list[str]
    learning_order: list[str]
    suggested_project: str
    resources: list[dict]
    has_detailed_guide: bool


def _fuzzy_lookup(skill: str, data: dict) -> dict | None:
    """
    Try exact lookup first, then fuzzy lookup in the recommendations dict.
    Returns the recommendation dict or None.
    """
    if skill in data:
        return data[skill]
    # Strip trailing 's' for simple plurals
    if skill.rstrip("s") in data:
        return data[skill.rstrip("s")]
    # Fuzzy lookup on keys
    keys = list(data.keys())
    if keys:
        match = process.extractOne(skill, keys, scorer=fuzz.token_set_ratio, score_cutoff=80)
        if match:
            return data[match[0]]
    return None


def get_skill_gap_recommendations(missing_skills: list[str]) -> list[dict]:
    """
    For each missing skill, return a structured learning recommendation.

    The recommendation includes:
      - why_it_matters: short explanation of the skill's importance
      - prerequisites: skills to learn first
      - learning_order: ordered sub-topics list
      - suggested_project: a concrete practice idea
      - resources: list of {title, url} (only reliable, known URLs)
      - has_detailed_guide: True when detailed data is available locally

    Returns a list of dicts (JSON-serialisable).
    """
    recommendations = []
    for skill in missing_skills:
        rec_data = _fuzzy_lookup(skill, _SKILL_REC)
        if rec_data:
            recommendations.append({
                "skill": skill,
                "why_it_matters": rec_data.get("why_it_matters", f"'{skill}' is a commonly required skill for this role."),
                "prerequisites": rec_data.get("prerequisites", []),
                "learning_order": rec_data.get("learning_order", []),
                "suggested_project": rec_data.get("suggested_project", "Build a small practice project using this technology."),
                "resources": rec_data.get("resources", []),
                "has_detailed_guide": True,
            })
        else:
            # Provide a generic entry for skills not in our recommendation DB
            recommendations.append({
                "skill": skill,
                "why_it_matters": f"'{skill}' is listed as a requirement in this job description.",
                "prerequisites": [],
                "learning_order": [f"Search for beginner tutorials on '{skill}'", f"Complete an introductory project using '{skill}'"],
                "suggested_project": f"Build a small demo application that uses '{skill}'.",
                "resources": [],
                "has_detailed_guide": False,
            })
    return recommendations


# ─────────────────────────────────────────────────────────────────────────────
# Job-Role Matching
# ─────────────────────────────────────────────────────────────────────────────

def _compute_role_score(
    resume_skills: set[str],
    required: list[str],
    preferred: list[str],
) -> tuple[float, float, float]:
    """
    Returns (overall_score, required_coverage, preferred_coverage) — all 0–100.

    Scoring formula (transparent):
      required_coverage  = matched_required / total_required * 100
      preferred_coverage = matched_preferred / total_preferred * 100  (0 if none)
      overall_score      = 0.70 * required_coverage + 0.30 * preferred_coverage

    Rationale for weights:
      - Required skills are non-negotiable; preferred are a bonus.
      - 70/30 split reflects typical job description language.
    """
    # Fuzzy matching: resume skill fuzzy-matches a role skill at >= 85 ratio
    def _match_count(role_skills: list[str]) -> int:
        count = 0
        for rs in role_skills:
            if rs in resume_skills:
                count += 1
                continue
            best = process.extractOne(
                rs, list(resume_skills),
                scorer=fuzz.token_sort_ratio,
                score_cutoff=85,
            )
            if best:
                count += 1
        return count

    req_count = len(required)
    pref_count = len(preferred)

    req_matched = _match_count(required) if req_count else 0
    pref_matched = _match_count(preferred) if pref_count else 0

    req_coverage = (req_matched / req_count * 100) if req_count else 0.0
    pref_coverage = (pref_matched / pref_count * 100) if pref_count else 0.0

    overall = round(0.70 * req_coverage + 0.30 * pref_coverage, 2)
    return overall, round(req_coverage, 2), round(pref_coverage, 2)


def _matched_and_missing(
    resume_skills: set[str],
    role_skills: list[str],
) -> tuple[list[str], list[str]]:
    matched: list[str] = []
    missing: list[str] = []
    for rs in role_skills:
        if rs in resume_skills:
            matched.append(rs)
            continue
        best = process.extractOne(
            rs, list(resume_skills),
            scorer=fuzz.token_sort_ratio,
            score_cutoff=85,
        )
        if best:
            matched.append(rs)
        else:
            missing.append(rs)
    return matched, missing


def get_role_recommendations(resume_skills: list[str], top_n: int = 5) -> list[dict]:
    """
    Compare resume skills against each job role profile and return the top N matches.

    Returns list of dicts (JSON-serialisable):
      {
        role, description, icon,
        overall_score,         -- 0–100 (70% required + 30% preferred)
        required_coverage,     -- 0–100
        preferred_coverage,    -- 0–100
        matched_required,      -- list[str] — required skills found
        missing_required,      -- list[str] — required skills NOT found
        matched_preferred,     -- list[str] — preferred skills found
        missing_preferred,     -- list[str] — preferred skills NOT found
        related_roles,
      }

    Note: these scores indicate skill overlap, not the probability of being hired.
    """
    if not _JOB_ROLES:
        return []

    resume_set = set(resume_skills)
    results: list[dict] = []

    for role_def in _JOB_ROLES:
        required: list[str] = role_def.get("required_skills", [])
        preferred: list[str] = role_def.get("preferred_skills", [])

        overall, req_cov, pref_cov = _compute_role_score(resume_set, required, preferred)
        matched_req, missing_req = _matched_and_missing(resume_set, required)
        matched_pref, missing_pref = _matched_and_missing(resume_set, preferred)

        results.append({
            "role": role_def.get("role", "Unknown"),
            "description": role_def.get("description", ""),
            "icon": role_def.get("icon", "🔹"),
            "overall_score": overall,
            "required_coverage": req_cov,
            "preferred_coverage": pref_cov,
            "matched_required": matched_req,
            "missing_required": missing_req,
            "matched_preferred": matched_pref,
            "missing_preferred": missing_pref,
            "related_roles": role_def.get("related_roles", []),
        })

    # Sort by overall_score descending, then required_coverage descending
    results.sort(key=lambda r: (-r["overall_score"], -r["required_coverage"]))
    return results[:top_n]


# ─────────────────────────────────────────────────────────────────────────────
# Explainability Narrative Generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_score_explanation(
    matched_skills: list[str],
    missing_skills: list[str],
    skill_match_score: float,
    text_similarity_score: float,
    final_score: float,
) -> list[str]:
    """
    Generate plain-English explanations for the match score.
    Uses only real data — no fabrication.

    Returns a list of explanation strings.
    """
    lines: list[str] = []

    # Overall summary
    total = len(matched_skills) + len(missing_skills)
    if total == 0:
        lines.append("No skills were extracted from the job description, so a meaningful score cannot be computed.")
        return lines

    pct = round(len(matched_skills) / total * 100)
    lines.append(
        f"Your resume matches {len(matched_skills)} out of {total} skills "
        f"identified in the job description ({pct}% skill coverage)."
    )

    # Skill match detail
    if matched_skills:
        sample = ", ".join(matched_skills[:5])
        more = f" and {len(matched_skills) - 5} more" if len(matched_skills) > 5 else ""
        lines.append(f"Skills found in your resume: {sample}{more}.")

    if missing_skills:
        sample = ", ".join(missing_skills[:5])
        more = f" and {len(missing_skills) - 5} more" if len(missing_skills) > 5 else ""
        lines.append(f"Skills listed in the job description but NOT detected in your resume: {sample}{more}.")

    # Score formula explanation
    lines.append(
        f"The final score of {final_score:.1f}% is calculated as: "
        f"60% × skill match ({skill_match_score:.1f}%) + 40% × text similarity ({text_similarity_score:.1f}%). "
        "Text similarity measures how closely the overall language of your resume matches the job description "
        "using TF-IDF cosine similarity."
    )

    # Caveats
    if total < 5:
        lines.append(
            "⚠️ The job description contains very few identifiable skills. "
            "Scores may be unreliable for short or vague job descriptions."
        )

    lines.append(
        "📌 This score reflects textual similarity and skill keyword overlap only. "
        "It does not predict interview outcomes, hiring decisions, or professional competence."
    )

    return lines
