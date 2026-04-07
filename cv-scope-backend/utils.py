"""
utils.py  —  CVScope NLP Pipeline (v2)
=======================================
4-layer architecture:
  Layer 1 — Text extraction         (PDF / DOCX)
  Layer 2 — Section-aware parsing   (isolate Skills / Experience sections)
    Layer 3 — Multi-pass skill extraction
                        (PhraseMatcher → NER → noun-chunks → YAKE keyphrases)
  Layer 4 — Normalization, matching & scoring

Dependencies: spacy, rapidfuzz, scikit-learn, pdfplumber, python-docx
Optional: yake (lightweight keyphrase extraction for unknown skills)

Performance note:
  A SINGLE shared spaCy pipeline (all components enabled) is loaded once
  at module import time via warmup_models(). All three extraction passes
  reuse the same nlp object — no repeated model loading per request.
"""

from __future__ import annotations

import io
import logging
import re
from dataclasses import dataclass
from typing import Literal, NamedTuple

import pdfplumber
import docx
import spacy
from spacy.matcher import PhraseMatcher
from rapidfuzz import fuzz, process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skill_taxonomy import ALIAS_MAP, CANONICAL_SKILLS

try:
    import yake  # type: ignore
except ImportError:  # pragma: no cover
    yake = None  # type: ignore

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Startup — single shared spaCy model (loaded ONCE, reused for all passes)
# ─────────────────────────────────────────────────────────────────────────────

_NLP: spacy.Language | None = None
_MATCHER: PhraseMatcher | None = None
_YAKE_EXTRACTOR = None


def warmup_models() -> None:
    """
    Pre-load all NLP resources at server startup.
    Call this from FastAPI's @app.on_event('startup') so the first
    user request is NOT slow.
    """
    global _NLP, _MATCHER
    if _NLP is not None:
        return  # already warmed up

    logger.info("CVScope: loading spaCy en_core_web_sm …")
    # Single pipeline with all components — used for NER + noun-chunks + PhraseMatcher
    _NLP = spacy.load("en_core_web_sm")
    _MATCHER = _build_phrase_matcher(_NLP)
    logger.info(
        "CVScope: NLP ready — %d canonical skills, %d aliases",
        len(CANONICAL_SKILLS),
        len(ALIAS_MAP),
    )


def _get_nlp() -> spacy.Language:
    if _NLP is None:
        warmup_models()
    return _NLP  # type: ignore[return-value]


def _get_matcher() -> PhraseMatcher:
    if _MATCHER is None:
        warmup_models()
    return _MATCHER  # type: ignore[return-value]


def _build_phrase_matcher(nlp: spacy.Language) -> PhraseMatcher:
    """Register every alias from the taxonomy as a phrase pattern."""
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [
        nlp.make_doc(alias)
        for aliases in CANONICAL_SKILLS.values()
        for alias in aliases
        if alias.strip()
    ]
    matcher.add("SKILL", patterns)
    return matcher


def _get_yake_extractor():
    """Create and cache the YAKE keyword extractor (if installed)."""
    global _YAKE_EXTRACTOR
    if yake is None:
        return None
    if _YAKE_EXTRACTOR is None:
        _YAKE_EXTRACTOR = yake.KeywordExtractor(
            lan="en",
            n=3,
            top=40,
            dedupLim=0.9,
        )
    return _YAKE_EXTRACTOR


# ─────────────────────────────────────────────────────────────────────────────
# Layer 1 — Text Extraction
# ─────────────────────────────────────────────────────────────────────────────

def extract_text(file) -> str:
    """
    Extract plain text from an UploadFile (PDF or DOCX).
    Reads into BytesIO to avoid stream cursor issues with spooled temp files.
    """
    filename: str = file.filename.lower()
    raw = file.file.read()

    if filename.endswith(".pdf"):
        text_parts: list[str] = []
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)

    elif filename.endswith(".docx"):
        doc = docx.Document(io.BytesIO(raw))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    return ""


# ─────────────────────────────────────────────────────────────────────────────
# Layer 2 — Section-Aware Parsing
# ─────────────────────────────────────────────────────────────────────────────

_SECTION_HEADERS = re.compile(
    r"(?im)^[ \t]*("
    r"skills?|technical skills?|core competencies?|technologies|tools?|tech stack|"
    r"experience|work experience|professional experience|"
    r"education|academic|projects?|certifications?|achievements?|"
    r"requirements?|responsibilities|qualifications?|"
    r"summary|objective|about me|languages?"
    r")\s*[:\-–—]?\s*$"
)


def _section_role(section_name: str) -> str:
    """Map a raw header string to a coarse role for weighting."""
    name = section_name.lower()
    if any(k in name for k in ("skill", "competenc", "technical", "technolog", "tool", "stack")):
        return "skills"
    if "project" in name:
        return "projects"
    if "experience" in name or "work" in name:
        return "experience"
    if "education" in name or "academic" in name:
        return "education"
    return "other"


def _group_sections_by_role(text: str) -> dict[str, str]:
    """Group split sections into coarse roles (skills/experience/projects/...)."""
    raw_sections = _split_into_sections(text)
    grouped: dict[str, list[str]] = {"skills": [], "experience": [], "projects": [], "education": [], "other": []}
    for section_name, section_text in raw_sections.items():
        role = _section_role(section_name)
        if section_text.strip():
            grouped[role].append(section_text.strip())
    return {k: "\n".join(v).strip() for k, v in grouped.items()}


def _split_into_sections(text: str) -> dict[str, str]:
    """Split resume text into named sections → {section_name: section_text}."""
    sections: dict[str, str] = {}
    lines = text.split("\n")
    current_section = "header"
    buffer: list[str] = []

    for line in lines:
        m = _SECTION_HEADERS.match(line.strip())
        if m:
            sections[current_section] = "\n".join(buffer).strip()
            current_section = m.group(1).lower().rstrip("s").strip()
            buffer = []
        else:
            buffer.append(line)

    sections[current_section] = "\n".join(buffer).strip()
    return sections


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

_GENERIC_NOISE: frozenset[str] = frozenset({
    "experience", "requirement", "responsibility", "description", "overview",
    "summary", "objective", "profile", "qualification", "candidate", "company",
    "team", "role", "position", "opportunity", "responsibilities", "knowledge",
    "understanding", "ability", "skill", "skills", "excellent", "strong",
    "good", "great", "best", "new", "current", "include", "work", "working",
    "years", "year", "month", "development", "management", "communication",
    "leadership", "problem", "solution", "time", "tools", "tool", "multiple",
    "various", "different", "following", "using", "make", "create", "build",
    "develop", "implement", "design", "maintain", "support", "provide",
    "ensure", "help", "use", "learn", "write", "read", "review", "test",
    "run", "set", "get", "put", "call", "send", "system", "application",
    "platform", "service", "product", "software", "hardware", "project",
    "process", "data", "user", "client", "server", "web", "app", "code",
    "base", "end", "full", "stack", "front", "back", "side", "level",
    "senior", "junior", "lead", "principal", "engineer", "developer",
    "intern", "analyst", "manager", "architect", "specialist",
})

_MIN_SKILL_LEN = 3   # avoids standalone noise like 'ci', 'os', 'db'


def _normalize_skill(raw: str) -> str | None:
    """Map a raw string to its canonical skill name, or None if it's noise."""
    cleaned = raw.strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)

    # Alias lookup FIRST so short-but-valid skills still work (js/ts/ml/go/c#/c++)
    if cleaned in ALIAS_MAP:
        return ALIAS_MAP[cleaned]

    stripped = cleaned.strip(".,;:/()")
    if stripped in ALIAS_MAP:
        return ALIAS_MAP[stripped]

    if len(cleaned) < _MIN_SKILL_LEN:
        return None
    if cleaned in _GENERIC_NOISE:
        return None
    if len(cleaned) > 30:
        return None

    return stripped if stripped else None


def _phrase_is_generic(phrase: str) -> bool:
    """Heuristic guard: drop phrases composed entirely of generic noise words."""
    tokens = re.findall(r"[a-z0-9\+\#\.\-]+", phrase.lower())
    if not tokens:
        return True
    return all(t in _GENERIC_NOISE for t in tokens)


def _techiness_multiplier(
    surface: str,
    *,
    source: str,
    section: str,
    ner_label: str | None = None,
) -> float:
    """Return a multiplicative factor that boosts tech-looking strings and downranks likely-noise."""
    s = surface.strip()
    if not s:
        return 0.0

    low = s.lower()
    if low in _GENERIC_NOISE:
        return 0.0

    if low.endswith((" inc", " ltd", " llc", " corp", " corporation", " limited")):
        return 0.0

    word_count = len(low.split())
    if word_count > 5:
        return 0.0

    # Acronyms (AWS, GCP, K8S)
    if s.isupper() and 2 <= len(s) <= 6:
        return 1.25

    has_digit = any(ch.isdigit() for ch in s)
    has_tech_punct = any(ch in "+#./-" for ch in s)
    if has_digit or has_tech_punct:
        return 1.15

    # Penalize ORG-looking TitleCase single tokens outside the Skills section
    if (
        source.startswith("ner")
        and ner_label == "ORG"
        and section != "skills"
        and word_count == 1
        and s[:1].isupper()
        and s[1:].islower()
    ):
        return 0.55

    # Multiword phrases are a bit noisier unless they look curated
    if word_count >= 3:
        stopy = {"and", "or", "with", "for", "to", "in", "of"}
        if any(w in stopy for w in low.split()):
            return 0.75
        return 0.9

    return 1.0


def _is_noise_token(token) -> bool:
    """True when a spaCy token is clearly not a skill word."""
    return token.pos_ in ("VERB", "AUX", "ADV", "DET", "CONJ", "PUNCT", "SPACE", "NUM") \
        or token.lemma_.lower() in _GENERIC_NOISE


# ─────────────────────────────────────────────────────────────────────────────
# Layer 3 — 3-Pass Skill Extraction Engine
# ─────────────────────────────────────────────────────────────────────────────

def _pass1_phrase_matcher(doc) -> set[str]:
    """
    Pass 1 — PhraseMatcher against full taxonomy.
    Highest confidence: catches exact and alias matches (ReactJS → react).
    """
    matcher = _get_matcher()
    found: set[str] = set()
    for _, start, end in matcher(doc):
        span_text = doc[start:end].text.lower()
        canonical = _normalize_skill(span_text)
        if canonical:
            found.add(canonical)
    return found


def _pass2_ner_fallback(doc) -> set[str]:
    """
    Pass 2 — NER entities (ORG / PRODUCT) as fallback for unknown/new tech.
    Catches things like 'Solidity', 'Bun', 'Temporal', 'Astro', etc.
    Guarded by length + noise filter + regex 'looks like tech' check.
    """
    found: set[str] = set()
    for ent in doc.ents:
        if ent.label_ not in ("ORG", "PRODUCT"):
            continue
        candidate = ent.text.strip()
        if not (3 <= len(candidate) <= 25):
            continue
        if candidate.lower() in _GENERIC_NOISE:
            continue

        normalized = _normalize_skill(candidate)
        if normalized:
            found.add(normalized)
        else:
            low = candidate.lower()
            # Keep raw if it matches a techy-looking pattern (no spaces, no generic words)
            if re.fullmatch(r"[a-z][a-z0-9\+\#\.\-]{2,20}", low) and low not in _GENERIC_NOISE:
                found.add(low)
    return found


def _pass3_noun_chunks(doc) -> set[str]:
    """
    Pass 3 — Noun chunks filtered by POS guard.
    Only run on the skills section text (already short) to reduce noise.
    Catches multi-word skills like 'machine learning', 'computer vision'.
    """
    found: set[str] = set()
    for chunk in doc.noun_chunks:
        tokens = [t for t in chunk if not _is_noise_token(t)]
        if not tokens:
            continue
        chunk_text = " ".join(t.text for t in tokens).strip().lower()
        if len(chunk_text) < _MIN_SKILL_LEN:
            continue
        normalized = _normalize_skill(chunk_text)
        if normalized:
            found.add(normalized)
    return found


@dataclass(frozen=True)
class SkillEvidence:
    skill: str
    surface: str
    source: str
    section: str
    confidence: float


class SkillExtractionResult(NamedTuple):
    skills: list[str]
    details: list[dict]
    confidence_by_skill: dict[str, float]


_SECTION_WEIGHTS_RESUME: dict[str, float] = {
    "skills": 1.0,
    "projects": 0.85,
    "experience": 0.75,
    "education": 0.45,
    "other": 0.35,
}

_SECTION_WEIGHTS_JD: dict[str, float] = {
    "skills": 1.0,
    "projects": 1.0,
    "experience": 1.0,
    "education": 1.0,
    "other": 1.0,
}

_ROLE_CHAR_LIMITS: dict[str, int] = {
    "skills": 4_000,
    "projects": 7_000,
    "experience": 7_000,
    "education": 3_000,
    "other": 10_000,
}


def _make_evidence(
    *,
    surface: str,
    source: str,
    section: str,
    section_weight: float,
    base_confidence: float,
    ner_label: str | None = None,
    extra_factor: float = 1.0,
) -> SkillEvidence | None:
    canonical = _normalize_skill(surface)
    if canonical is None:
        return None
    if _phrase_is_generic(canonical):
        # Prevent generic phrases from YAKE/chunks/NER becoming false skills
        # (canonical will already be lowercased/cleaned)
        if canonical not in CANONICAL_SKILLS:
            return None

    tech_mult = _techiness_multiplier(surface, source=source, section=section, ner_label=ner_label)
    if tech_mult <= 0.0:
        return None

    confidence = min(1.0, base_confidence * section_weight * tech_mult * extra_factor)
    return SkillEvidence(
        skill=canonical,
        surface=surface.strip(),
        source=source,
        section=section,
        confidence=float(round(float(confidence), 4)),
    )


def _pass1_phrase_matcher_evidence(doc, *, section: str, section_weight: float) -> list[SkillEvidence]:
    matcher = _get_matcher()
    out: list[SkillEvidence] = []
    for _, start, end in matcher(doc):
        surface = doc[start:end].text
        ev = _make_evidence(
            surface=surface,
            source="taxonomy",
            section=section,
            section_weight=section_weight,
            base_confidence=0.95,
        )
        if ev:
            out.append(ev)
    return out


def _pass2_ner_evidence(doc, *, section: str, section_weight: float) -> list[SkillEvidence]:
    out: list[SkillEvidence] = []
    for ent in doc.ents:
        if ent.label_ not in ("ORG", "PRODUCT"):
            continue
        candidate = ent.text.strip()
        if not (3 <= len(candidate) <= 30):
            continue

        # If it normalizes to something known, keep it (e.g., Amazon Web Services → aws)
        normalized = _normalize_skill(candidate)
        if normalized and normalized in CANONICAL_SKILLS:
            ev = _make_evidence(
                surface=candidate,
                source="ner_normalized",
                section=section,
                section_weight=section_weight,
                base_confidence=0.82,
                ner_label=ent.label_,
            )
            if ev:
                out.append(ev)
            continue

        # Unknown skill candidates: be stricter to avoid company-name noise
        low = candidate.lower().strip()
        if low in _GENERIC_NOISE:
            continue
        if ent.label_ == "ORG" and section != "skills":
            # Outside Skills section, ORG is frequently company names → high false positives
            continue

        base = 0.65 if ent.label_ == "PRODUCT" else 0.5
        ev = _make_evidence(
            surface=candidate,
            source=f"ner_{ent.label_.lower()}_unknown",
            section=section,
            section_weight=section_weight,
            base_confidence=base,
            ner_label=ent.label_,
        )
        if ev and ev.confidence >= 0.35:
            out.append(ev)
    return out


def _pass3_noun_chunks_evidence(doc, *, section: str, section_weight: float) -> list[SkillEvidence]:
    out: list[SkillEvidence] = []
    for chunk in doc.noun_chunks:
        tokens = [t for t in chunk if not _is_noise_token(t)]
        if not tokens:
            continue
        chunk_text = " ".join(t.text for t in tokens).strip()
        if len(chunk_text) < _MIN_SKILL_LEN:
            continue
        ev = _make_evidence(
            surface=chunk_text,
            source="noun_chunk",
            section=section,
            section_weight=section_weight,
            base_confidence=0.55,
        )
        if ev and ev.confidence >= 0.4:
            out.append(ev)
    return out


def _pass4_yake_evidence(text: str, *, section: str, section_weight: float) -> list[SkillEvidence]:
    extractor = _get_yake_extractor()
    if extractor is None:
        return []
    if not text or not text.strip():
        return []

    out: list[SkillEvidence] = []
    try:
        keywords = extractor.extract_keywords(text)
    except Exception:
        return []

    for phrase, score in keywords:
        phrase = str(phrase).strip()
        if not phrase:
            continue
        if not (3 <= len(phrase) <= 40):
            continue

        # YAKE score is lower-is-better; map roughly into (0..1]
        yake_factor = float(1.0 / (1.0 + (float(score) * 10.0)))

        ev = _make_evidence(
            surface=phrase,
            source="yake",
            section=section,
            section_weight=section_weight,
            base_confidence=0.6,
            extra_factor=min(1.0, 0.5 + 0.8 * yake_factor),
        )
        if ev and ev.confidence >= 0.35:
            out.append(ev)
    return out


def extract_skills_detailed(
    text: str,
    *,
    doc_type: Literal["resume", "job_description"] = "resume",
) -> SkillExtractionResult:
    """Extract skills + a compact explainability payload (confidence + provenance)."""
    if not text or not text.strip():
        return SkillExtractionResult([], [], {})

    nlp = _get_nlp()
    grouped = _group_sections_by_role(text)
    weights = _SECTION_WEIGHTS_RESUME if doc_type == "resume" else _SECTION_WEIGHTS_JD

    role_texts: list[tuple[str, str]] = []
    for role in ("skills", "projects", "experience", "education", "other"):
        chunk = grouped.get(role, "").strip()
        if not chunk:
            continue
        role_texts.append((role, chunk[:_ROLE_CHAR_LIMITS.get(role, 5_000)]))

    docs = list(nlp.pipe([t for _, t in role_texts]))
    evidences: list[SkillEvidence] = []
    skills_role_text = grouped.get("skills", "").strip()

    for (role, _), doc in zip(role_texts, docs):
        section_weight = weights.get(role, 1.0)
        evidences.extend(_pass1_phrase_matcher_evidence(doc, section=role, section_weight=section_weight))
        evidences.extend(_pass2_ner_evidence(doc, section=role, section_weight=section_weight))
        if role == "skills":
            evidences.extend(_pass3_noun_chunks_evidence(doc, section=role, section_weight=section_weight))

    # YAKE is strongest on curated lists (Skills). For JDs, fall back to full text.
    yake_input = skills_role_text
    yake_section = "skills"
    if doc_type == "job_description" and not yake_input:
        yake_input = text[:10_000]
        yake_section = "other"

    evidences.extend(_pass4_yake_evidence(yake_input, section=yake_section, section_weight=weights.get(yake_section, 1.0)))

    # Aggregate to skill-level details
    aggregates: dict[str, dict] = {}
    for ev in evidences:
        agg = aggregates.get(ev.skill)
        if agg is None:
            aggregates[ev.skill] = {
                "skill": ev.skill,
                "confidence": ev.confidence,
                "sources": {ev.source},
                "sections": {ev.section},
                "surface_forms": {ev.surface},
            }
        else:
            agg["confidence"] = max(float(agg["confidence"]), float(ev.confidence))
            agg["sources"].add(ev.source)
            agg["sections"].add(ev.section)
            agg["surface_forms"].add(ev.surface)

    details: list[dict] = []
    confidence_by_skill: dict[str, float] = {}
    for skill, agg in aggregates.items():
        # Small boost for multi-source agreement
        boost = 0.05 * max(0, len(agg["sources"]) - 1)
        final_conf = float(round(min(1.0, float(agg["confidence"]) + boost), 4))
        confidence_by_skill[skill] = final_conf

        details.append({
            "skill": skill,
            "confidence": final_conf,
            "sources": sorted(agg["sources"]),
            "sections": sorted(agg["sections"]),
            "surface_forms": sorted(agg["surface_forms"])[:3],
        })

    # Filter out low-confidence unknowns (keep all known taxonomy skills)
    filtered_details: list[dict] = []
    for d in details:
        if d["skill"] in CANONICAL_SKILLS or float(d["confidence"]) >= 0.35:
            filtered_details.append(d)

    filtered_details.sort(key=lambda d: (-float(d["confidence"]), str(d["skill"])))
    skills = sorted(d["skill"] for d in filtered_details)
    confidence_by_skill = {k: v for k, v in confidence_by_skill.items() if k in set(skills)}

    return SkillExtractionResult(skills=skills, details=filtered_details, confidence_by_skill=confidence_by_skill)


def _deduplicate(skills: list[str]) -> list[str]:
    """
    Remove near-duplicates using rapidfuzz token_sort_ratio ≥ 90.
    When two skills are near-dupes, keep the shorter/canonical one.
    """
    if not skills:
        return []
    unique: list[str] = []
    for skill in skills:
        is_dup = False
        for i, kept in enumerate(unique):
            if fuzz.token_sort_ratio(skill, kept) >= 90:
                if len(skill) < len(kept):
                    unique[i] = skill   # replace with the shorter form
                is_dup = True
                break
        if not is_dup:
            unique.append(skill)
    return unique


def extract_skills(text: str) -> list[str]:
    """
    Main extraction function — orchestrates all 3 passes.

    Strategy:
      1. Section-aware split: identify Skills section (highest signal)
      2. Pass 1 (PhraseMatcher): known skills on full text
      3. Pass 2 (NER): unknown tech entities on full text
      4. Pass 3 (noun chunks): multi-word skills on skills section only
      5. Deduplicate → safety filter → sort
    """
    return extract_skills_detailed(text, doc_type="resume").skills


# ─────────────────────────────────────────────────────────────────────────────
# Layer 4 — Matching & Scoring
# ─────────────────────────────────────────────────────────────────────────────

class MatchResult(NamedTuple):
    matched: list[str]
    missing: list[str]


def match_skills(resume_skills: list[str], jd_skills: list[str]) -> MatchResult:
    """
    Three-pass matching:
      Pass 1 — Exact canonical match
      Pass 2 — Fuzzy match (rapidfuzz token_sort_ratio ≥ 85)
      Pass 3 — Falls to missing
    """
    if not jd_skills:
        return MatchResult([], [])

    resume_set = set(resume_skills)
    matched: list[str] = []
    missing: list[str] = []

    for jd_skill in jd_skills:
        # Pass 1 — exact
        if jd_skill in resume_set:
            matched.append(jd_skill)
            continue

        # Pass 2 — fuzzy
        best = process.extractOne(
            jd_skill,
            resume_skills,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=85,
        )
        if best is not None:
            matched.append(jd_skill)
        else:
            missing.append(jd_skill)

    return MatchResult(matched=matched, missing=missing)


def calculate_similarity(
    resume_skills: list[str],
    jd_skills: list[str],
    resume_text: str = "",
    jd_text: str = "",
    jd_skill_weights: dict[str, float] | None = None,
) -> dict:
    """
    Weighted similarity score with full breakdown:

      skill_match_score  = (matched_count / jd_skill_count) × 100   [60% weight]
      text_similarity    = TF-IDF cosine on full raw texts           [40% weight]
      final_score        = 0.6 × skill_match + 0.4 × text_similarity

    All values guaranteed to be Python float (not np.float64) for JSON safety.
    """
    if not jd_skills:
        return {"skill_match_score": 0.0, "text_similarity_score": 0.0, "final_score": 0.0}

    # ── Skill match score ─────────────────────────────────────────────────────
    result = match_skills(resume_skills, jd_skills)

    # Prefer confidence-weighted JD skill coverage when available.
    if jd_skill_weights:
        total_w = float(sum(max(0.05, float(jd_skill_weights.get(s, 0.5))) for s in jd_skills))
        matched_w = float(sum(max(0.05, float(jd_skill_weights.get(s, 0.5))) for s in result.matched))
        skill_match_pct = float(round((matched_w / total_w) * 100, 2)) if total_w > 0 else 0.0
        skill_match_unweighted = float(round(len(result.matched) / len(jd_skills) * 100, 2))
    else:
        skill_match_pct = float(round(len(result.matched) / len(jd_skills) * 100, 2))
        skill_match_unweighted = skill_match_pct

    # ── TF-IDF on full texts ──────────────────────────────────────────────────
    doc_b = jd_text.strip() or " ".join(jd_skills)
    doc_full = resume_text.strip() or " ".join(resume_skills)

    grouped = _group_sections_by_role(resume_text) if resume_text.strip() else {}
    resume_skills_text = (grouped.get("skills", "").strip() or " ".join(resume_skills))[:4_000]
    resume_exp_text = (
        "\n".join([
            grouped.get("experience", "").strip(),
            grouped.get("projects", "").strip(),
        ])
        .strip()
    )[:8_000]
    doc_full = doc_full[:12_000]
    doc_b = doc_b[:12_000]

    text_similarity_full = 0.0
    text_similarity_skills = 0.0
    text_similarity_experience = 0.0
    text_similarity = 0.0

    if doc_full and doc_b:
        try:
            docs: list[str] = [doc_b, doc_full, resume_skills_text]
            labels: list[str] = ["jd", "full", "skills"]
            if resume_exp_text:
                docs.append(resume_exp_text)
                labels.append("experience")

            vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                min_df=1,
                stop_words="english",
                max_features=8000,
            )
            matrix = vectorizer.fit_transform(docs)
            jd_vec = matrix[0:1]

            def _cos(i: int) -> float:
                return float(cosine_similarity(jd_vec, matrix[i:i+1])[0][0])

            sims: dict[str, float] = {
                "full": _cos(labels.index("full")),
                "skills": _cos(labels.index("skills")),
            }
            if "experience" in labels:
                sims["experience"] = _cos(labels.index("experience"))
            else:
                sims["experience"] = 0.0

            text_similarity_full = float(round(sims["full"] * 100, 2))
            text_similarity_skills = float(round(sims["skills"] * 100, 2))
            text_similarity_experience = float(round(sims["experience"] * 100, 2))

            weights = {"skills": 0.5, "experience": 0.3, "full": 0.2}
            available = {k for k in ("skills", "experience", "full") if (k != "experience" or resume_exp_text)}
            effective = {k: v for k, v in weights.items() if k in available}
            norm = sum(effective.values()) or 1.0
            effective = {k: v / norm for k, v in effective.items()}

            weighted = (
                effective.get("skills", 0.0) * sims["skills"]
                + effective.get("experience", 0.0) * sims["experience"]
                + effective.get("full", 0.0) * sims["full"]
            )
            text_similarity = float(round(weighted * 100, 2))
        except Exception as e:
            logger.warning("Section-weighted TF-IDF similarity failed: %s", e)
            text_similarity = 0.0

    # ── Weighted final score ──────────────────────────────────────────────────
    final_score = float(round(0.6 * skill_match_pct + 0.4 * text_similarity, 2))

    return {
        "skill_match_score": skill_match_pct,
        "skill_match_unweighted": skill_match_unweighted,
        "text_similarity_score": text_similarity,
        "text_similarity_full": text_similarity_full,
        "text_similarity_skills": text_similarity_skills,
        "text_similarity_experience": text_similarity_experience,
        "final_score": final_score,
    }