"""
evaluate.py  —  CVScope Local Evaluation Script
================================================
Measures skill extraction precision, recall, F1-score, and matching accuracy
on a locally stored synthetic dataset (tests/evaluation_dataset.json).

Usage:
    cd cv-scope-backend
    python evaluate.py

No external services, no GPU, no internet connection required.

─────────────────────────────────────────────────────────────────────────────
IMPORTANT CAVEAT
─────────────────────────────────────────────────────────────────────────────
The evaluation dataset is SYNTHETIC — created manually for testing purposes.
Results reflect performance on these specific examples, not general resumes.
False positives (extra skills extracted) and false negatives (missed skills)
are discussed in the output. Real-world performance will differ.

─────────────────────────────────────────────────────────────────────────────
METRICS EXPLAINED
─────────────────────────────────────────────────────────────────────────────
Precision (P)  = TP / (TP + FP)
               = fraction of extracted skills that are genuinely expected

Recall (R)     = TP / (TP + FN)
               = fraction of expected skills that were successfully extracted

F1-score       = 2 × (P × R) / (P + R)
               = harmonic mean of precision and recall

  TP = skill extracted AND in expected list
  FP = skill extracted but NOT in expected list (false alarm)
  FN = skill in expected list but NOT extracted (missed)

For matching tests:
  Exact match accuracy = fraction of (matched, missing) pairs that exactly
  match the expected (matched, missing) sets.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# Add parent directory to sys.path so we can import project modules
_HERE = Path(__file__).parent
_BACKEND = _HERE.parent if _HERE.name == "tests" else _HERE
sys.path.insert(0, str(_BACKEND))

from utils import extract_skills_detailed, match_skills, warmup_models


# ─────────────────────────────────────────────────────────────────────────────
# Load dataset
# ─────────────────────────────────────────────────────────────────────────────

def _load_dataset() -> dict:
    dataset_path = _HERE / "evaluation_dataset.json"
    if not dataset_path.exists():
        dataset_path = _BACKEND / "tests" / "evaluation_dataset.json"
    with open(dataset_path, encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────────────────────
# Evaluation Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    """Return (precision, recall, f1) as floats in [0, 1]."""
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return precision, recall, f1


def _print_separator(char: str = "─", width: int = 70) -> None:
    print(char * width)


def _print_header(title: str) -> None:
    _print_separator("═")
    print(f"  {title}")
    _print_separator("═")


# ─────────────────────────────────────────────────────────────────────────────
# Skill Extraction Evaluation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_skill_extraction(tests: list[dict]) -> dict:
    print()
    _print_header("SKILL EXTRACTION EVALUATION")
    print(f"  {'ID':<10} {'P':>6} {'R':>6} {'F1':>6}  {'TP':>4} {'FP':>4} {'FN':>4}  Notes")
    _print_separator()

    totals = {"tp": 0, "fp": 0, "fn": 0}
    results = []

    for test in tests:
        test_id = test["id"]
        doc_type = test.get("doc_type", "resume")
        text = test["text"]
        expected: set[str] = set(test.get("expected_skills", []))
        notes = test.get("notes", "")

        extraction = extract_skills_detailed(text, doc_type=doc_type)
        extracted: set[str] = set(extraction.skills)

        tp = len(extracted & expected)
        fp = len(extracted - expected)
        fn = len(expected - extracted)
        p, r, f1 = _prf(tp, fp, fn)

        totals["tp"] += tp
        totals["fp"] += fp
        totals["fn"] += fn

        flag = ""
        if fp > 0:
            flag = f"  [FP: {sorted(extracted - expected)}]"
        if fn > 0:
            flag += f"  [FN: {sorted(expected - extracted)}]"

        print(f"  {test_id:<10} {p:>6.3f} {r:>6.3f} {f1:>6.3f}  {tp:>4} {fp:>4} {fn:>4}  {notes}")
        if flag:
            print(f"  {'':10} {flag}")

        results.append({"id": test_id, "precision": p, "recall": r, "f1": f1, "tp": tp, "fp": fp, "fn": fn})

    _print_separator()
    macro_p = sum(r["precision"] for r in results) / len(results) if results else 0.0
    macro_r = sum(r["recall"] for r in results) / len(results) if results else 0.0
    macro_f1 = sum(r["f1"] for r in results) / len(results) if results else 0.0

    # Micro averages (aggregate TP/FP/FN across all tests)
    micro_p, micro_r, micro_f1 = _prf(totals["tp"], totals["fp"], totals["fn"])

    print(f"\n  Macro averages  — P: {macro_p:.3f}  R: {macro_r:.3f}  F1: {macro_f1:.3f}")
    print(f"  Micro averages  — P: {micro_p:.3f}  R: {micro_r:.3f}  F1: {micro_f1:.3f}")
    print(f"  Totals          — TP: {totals['tp']}  FP: {totals['fp']}  FN: {totals['fn']}")

    return {
        "macro_precision": macro_p,
        "macro_recall": macro_r,
        "macro_f1": macro_f1,
        "micro_precision": micro_p,
        "micro_recall": micro_r,
        "micro_f1": micro_f1,
        "per_test": results,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Skill Matching Evaluation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_skill_matching(tests: list[dict]) -> dict:
    print()
    _print_header("SKILL MATCHING EVALUATION")
    print(f"  {'ID':<10} {'Matched?':>10}  {'Missing?':>10}  Notes")
    _print_separator()

    exact_match_count = 0
    results = []

    for test in tests:
        test_id = test["id"]
        resume_skills: list[str] = test["resume_skills"]
        jd_skills: list[str] = test["jd_skills"]
        expected_matched: set[str] = set(test["expected_matched"])
        expected_missing: set[str] = set(test["expected_missing"])
        notes = test.get("notes", "")

        result = match_skills(resume_skills, jd_skills)
        actual_matched: set[str] = set(result.matched)
        actual_missing: set[str] = set(result.missing)

        matched_ok = actual_matched == expected_matched
        missing_ok = actual_missing == expected_missing
        exact_match = matched_ok and missing_ok
        if exact_match:
            exact_match_count += 1

        matched_str = "✓" if matched_ok else f"✗ got {sorted(actual_matched)}"
        missing_str = "✓" if missing_ok else f"✗ got {sorted(actual_missing)}"

        print(f"  {test_id:<10} {matched_str:<12}  {missing_str:<12}  {notes}")
        results.append({"id": test_id, "exact_match": exact_match})

    _print_separator()
    accuracy = exact_match_count / len(tests) if tests else 0.0
    print(f"\n  Exact match accuracy: {accuracy:.3f}  ({exact_match_count}/{len(tests)} tests passed)")

    return {"exact_match_accuracy": accuracy, "per_test": results}


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    _print_header("CVScope — Local Evaluation Script")
    print()
    print("  Dataset type : SYNTHETIC (manually created for testing)")
    print("  Warning      : Results on synthetic data may not reflect real-world performance.")
    print("  No GPU, no internet, no external services required.")

    print("\n  Loading NLP models …")
    t0 = time.perf_counter()
    warmup_models()
    t_load = time.perf_counter() - t0
    print(f"  Models loaded in {t_load:.2f}s")

    dataset = _load_dataset()
    se_tests = dataset.get("skill_extraction_tests", [])
    mt_tests = dataset.get("matching_tests", [])

    print(f"\n  Skill extraction tests : {len(se_tests)}")
    print(f"  Matching tests         : {len(mt_tests)}")

    t1 = time.perf_counter()
    se_results = evaluate_skill_extraction(se_tests)
    t_se = time.perf_counter() - t1

    t2 = time.perf_counter()
    mt_results = evaluate_skill_matching(mt_tests)
    t_mt = time.perf_counter() - t2

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    _print_header("SUMMARY")
    print(f"  Skill Extraction  — Micro F1: {se_results['micro_f1']:.3f}  "
          f"(P={se_results['micro_precision']:.3f}, R={se_results['micro_recall']:.3f})")
    print(f"  Skill Matching    — Exact match accuracy: {mt_results['exact_match_accuracy']:.3f}")
    print(f"  Runtime           — Extraction: {t_se:.2f}s  |  Matching: {t_mt:.2f}s  |  "
          f"Model load: {t_load:.2f}s")

    print()
    _print_header("LIMITATIONS & NOTES")
    print("""
  1. SYNTHETIC DATA: All test examples were created manually, not from real resumes.
     Performance on real-world documents may be higher or lower.

  2. FALSE POSITIVES: The NLP pipeline may extract organisational or generic terms
     as skills (e.g., company names detected as ORG entities). This inflates FP.

  3. FALSE NEGATIVES: Unusual abbreviations, novel technologies, or skills described
     in full sentences may be missed if not in the taxonomy.

  4. DATASET SIZE: 10 extraction tests are too small for reliable generalisation.
     A minimum of 50–100 annotated real resumes would be needed for robust evaluation.

  5. MATCH ACCURACY: Matching uses exact canonical comparison + fuzzy fallback.
     The 85% RapidFuzz threshold may be too strict for very short skill names
     (e.g., 'Go' vs 'Golang').
    """)


if __name__ == "__main__":
    main()
