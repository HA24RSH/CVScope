import { useEffect, useMemo, useState } from "react";
import SkillList from "./SkillList";

/* ── Helpers ─────────────────────────────────────────────────────────────── */
function clampPct(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return 0;
  return Math.max(0, Math.min(100, n));
}

function scoreLabel(pct) {
  if (pct >= 75) return { text: "Excellent Match", dot: "var(--color-primary-dark)" };
  if (pct >= 50) return { text: "Good Match",      dot: "var(--color-primary)" };
  if (pct >= 30) return { text: "Partial Match",   dot: "var(--color-muted)" };
  return               { text: "Needs Work",       dot: "var(--color-error)" };
}

function safeArray(v) {
  return Array.isArray(v) ? v : [];
}

function fallbackResourcesFor(skill) {
  const q = encodeURIComponent(`${skill} tutorial`);
  const s = encodeURIComponent(skill);
  return [
    {
      title: "Search on YouTube",
      url: `https://www.youtube.com/results?search_query=${q}`,
      type: "video",
      free: true,
    },
    {
      title: "Search on freeCodeCamp",
      url: `https://www.freecodecamp.org/news/search/?query=${s}`,
      type: "tutorial",
      free: true,
    },
    {
      title: "roadmap.sh",
      url: "https://roadmap.sh/",
      type: "roadmap",
      free: true,
    },
  ];
}

function buildRecommendations({ missing, apiRecommendations }) {
  const missingList = safeArray(missing);
  const apiList = safeArray(apiRecommendations);

  const recBySkill = new Map();
  for (const rec of apiList) {
    if (!rec || typeof rec !== "object") continue;
    if (!rec.skill) continue;
    recBySkill.set(String(rec.skill), safeArray(rec.resources));
  }

  return missingList.map((skill) => {
    const resources = recBySkill.get(skill);
    return {
      skill,
      resources: (resources && resources.length > 0) ? resources : fallbackResourcesFor(skill),
    };
  });
}

/* ── Metric Bar ──────────────────────────────────────────────────────────── */
function MetricBar({ label, value, variant = "skill" }) {
  const pct = clampPct(value);
  return (
    <div className="metric">
      <div className="metric-top">
        <span className="metric-label">{label}</span>
        <span className="metric-value">{pct.toFixed(1)}%</span>
      </div>
      <div className="metric-track" aria-hidden="true">
        <div className={`metric-fill ${variant}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

/* ── Recommendations Accordion ───────────────────────────────────────────── */
function RecommendationsAccordion({ missingSkills, apiRecommendations }) {
  const missing = safeArray(missingSkills);
  const [openSkill, setOpenSkill] = useState(missing[0] || null);

  useEffect(() => {
    // When a new analysis arrives, ensure at least one skill is expanded
    // so the roadmap/resources are immediately visible.
    setOpenSkill((current) => {
      if (missing.length === 0) return null;
      if (current && missing.includes(current)) return current;
      return missing[0];
    });
  }, [missing]);

  const recs = useMemo(() => {
    return buildRecommendations({ missing, apiRecommendations });
  }, [missing, apiRecommendations]);

  if (missing.length === 0) return null;

  return (
    <div className="recs-section">
      <div className="recs-header-row">
        <div className="recs-title">Learning Roadmap</div>
        <div className="recs-count">{missing.length}</div>
      </div>

      {recs.map((rec) => {
        const open = openSkill === rec.skill;
        const resources = safeArray(rec.resources);
        return (
          <div className="acc-item" key={rec.skill}>
            <button
              className="acc-trigger"
              type="button"
              onClick={() => setOpenSkill(open ? null : rec.skill)}
              aria-expanded={open}
            >
              <span className="acc-skill-name">{rec.skill}</span>
              <span className="acc-resource-count">
                {resources.length} resource{resources.length !== 1 ? "s" : ""}
              </span>
              <svg
                className={`acc-chevron${open ? " open" : ""}`}
                viewBox="0 0 16 16"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M4 6l4 4 4-4" />
              </svg>
            </button>

            <div className={`acc-content${open ? " open" : ""}`}>
              {resources.map((r, idx) => {
                const type = (typeof r?.type === "string" ? r.type : "link").toUpperCase();
                return (
                  <a
                    className="rec-row"
                    key={idx}
                    href={r.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <span className="rec-row-left">
                      <span className="rec-type-badge">{type}</span>
                      <span className="rec-link-title">{r.title}</span>
                    </span>
                    {r.free && <span className="rec-free-tag">FREE</span>}
                  </a>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ── Result Card ─────────────────────────────────────────────────────────── */
function ResultCard({ result }) {
  if (!result) return null;

  const pct            = clampPct(result?.match_percentage ?? 0);
  const label          = scoreLabel(pct);
  const breakdown      = result?.similarity_breakdown ?? null;
  const resumeSkills   = safeArray(result?.resume_skills);
  const jobSkills      = safeArray(result?.job_skills);
  const matched        = safeArray(result?.matched_skills);
  const missing        = safeArray(result?.missing_skills);
  const recommendations = safeArray(result?.recommendations);

  return (
    <div className="card result-card">

      {/* ── Score Row ─────────────────────────────────────────────── */}
      <div className="result-score-row">
        <div className="score-numeral-wrap" aria-label={`Match score ${Math.round(pct)} percent`}>
          <div className="score-numeral">{Math.round(pct)}</div>
          <div className="score-unit">%</div>
        </div>

        <div className="score-meta">
          <div className="score-meta-label">Match score</div>
          <span className="match-badge">
            <span className="match-badge-dot" style={{ background: label.dot }} aria-hidden="true" />
            {label.text}
          </span>
        </div>
      </div>

      {/* ── Stats ─────────────────────────────────────────────────── */}
      <div className="stats-row">
        <div className="stat">
          <div className="stat-value">{jobSkills.length}</div>
          <div className="stat-label">JD skills</div>
        </div>
        <div className="stat">
          <div className="stat-value gold">{matched.length}</div>
          <div className="stat-label">Matched</div>
        </div>
        <div className="stat">
          <div className="stat-value" style={{ color: "var(--color-error)" }}>{missing.length}</div>
          <div className="stat-label">Missing</div>
        </div>
        <div className="stat">
          <div className="stat-value">{resumeSkills.length}</div>
          <div className="stat-label">Your skills</div>
        </div>
      </div>

      {/* ── Similarity Breakdown ───────────────────────────────────── */}
      {breakdown && (
        <div className="metrics">
          <div className="metrics-title">Similarity breakdown</div>
          <MetricBar label="Skill match score" value={breakdown.skill_match_score} variant="skill" />
          <MetricBar label="Text similarity"   value={breakdown.text_similarity_score} variant="text" />
        </div>
      )}

      {/* ── Learning Roadmap ───────────────────────────────────────── */}
      <RecommendationsAccordion missingSkills={missing} apiRecommendations={recommendations} />

      {/* ── Skill Breakdown ────────────────────────────────────────── */}
      <div className="skills-section-title">Skill breakdown</div>
      <div className="grid">
        <SkillList title="✅ Matched"      skills={matched}    variant="matched" />
        <SkillList title="❌ Missing"      skills={missing}    variant="missing" />
        <SkillList title="📋 JD Required"  skills={jobSkills}  variant="jd" />
        <SkillList title="👤 Your Resume"  skills={resumeSkills} variant="default" />
      </div>
    </div>
  );
}

export default ResultCard;
