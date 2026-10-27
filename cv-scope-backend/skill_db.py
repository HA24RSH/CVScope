"""
skill_db.py  —  DEPRECATED
===========================
This file was the original flat skill dictionary from CVScope v1.
It has been superseded by skill_taxonomy.py (v2+), which provides:

  - CANONICAL_SKILLS   : 220+ canonical skill names → alias lists
  - ALIAS_MAP          : flat alias → canonical name (O(1) lookup)
  - SKILL_CATEGORIES   : category → list of canonical skill names
  - SKILL_CATEGORY_MAP : canonical skill name → category (O(1) lookup)
  - get_skill_category : helper function

DO NOT import this module in new code.
It is kept here only for historical reference and will be removed
in a future version.
"""

import warnings

warnings.warn(
    "skill_db.py is deprecated and will be removed in a future version. "
    "Import from skill_taxonomy.py instead.",
    DeprecationWarning,
    stacklevel=2,
)

# ── Legacy stub (kept for reference only) ────────────────────────────────────
SKILLS = {
    "python": ["python"],
    "java": ["java"],
    "javascript": ["javascript", "js", "typescript"],
    "node": ["node", "node.js"],
    "react": ["react", "react.js"],
    "react native": ["react native"],
    "rest api": ["rest api", "api"],
    "sql": ["sql", "mysql", "postgresql"],
    "html": ["html"],
    "css": ["css"],
    "git": ["git", "github"],
    "docker": ["docker"],
    "aws": ["aws"],
    "express": ["express", "express.js"],
    "wordpress": ["wordpress"],
    "django": ["django"],
    "flask": ["flask"],
    "mongodb": ["mongodb", "mongo"],
    "firebase": ["firebase"],
    "graphql": ["graphql"],
    "next.js": ["next.js", "nextjs"],
}