import SkillList from "./SkillList";

/* ── Helpers ─────────────────────────────────────────────────────────────── */
function clampPct(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return 0;
  return Math.max(0, Math.min(100, n));
}

function scoreLabel(pct) {
  if (pct >= 70) return { text: "Excellent Match", cls: "excellent", emoji: "🎉" };
  if (pct >= 40) return { text: "Good Match",      cls: "good",      emoji: "✅" };
  return               { text: "Needs Work",        cls: "low",       emoji: "📈" };
}

/* ── Score Gauge ─────────────────────────────────────────────────────────── */
function ScoreGauge({ value }) {
  const pct          = clampPct(value);
  const stroke       = 9;
  const r            = 46;
  const circumference = 2 * Math.PI * r;
  const offset       = circumference * (1 - pct / 100);
  const label        = scoreLabel(pct);

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
      {/* Circular gauge */}
      <div className="score-gauge" aria-label={`Match score ${Math.round(pct)} percent`}>
        <svg viewBox="0 0 110 110" role="img">
          <defs>
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%"   stopColor="#6366f1" />
              <stop offset="100%" stopColor="#8b5cf6" />
            </linearGradient>
          </defs>
          <circle className="score-gauge-track"    cx="55" cy="55" r={r} strokeWidth={stroke} />
          <circle
            className="score-gauge-progress"
            cx="55" cy="55" r={r}
            strokeWidth={stroke}
            strokeDasharray={`${circumference} ${circumference}`}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="score-gauge-center">
          <div className="score-gauge-value">{Math.round(pct)}%</div>
          <div className="score-gauge-subtitle">Match</div>
        </div>
      </div>

      {/* Label beside gauge */}
      <div className="result-score-info">
        <div className="result-score-label">Overall Score</div>
        <div className="result-score-title">{label.emoji} {label.text}</div>
        <span className={`result-score-badge ${label.cls}`}>
          {pct >= 70 ? "Strong profile" : pct >= 40 ? "Competitive" : "Gap analysis below"}
        </span>
      </div>
    </div>
  );
}

/* ── Metric Bar ──────────────────────────────────────────────────────────── */
function MetricBar({ label, value }) {
  const pct = clampPct(value);
  return (
    <div className="metric">
      <div className="metric-top">
        <span className="metric-label">{label}</span>
        <span className="metric-value">{pct.toFixed(1)}%</span>
      </div>
      <div className="metric-track" aria-hidden="true">
        <div className="metric-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

/* ── Resource type badge ─────────────────────────────────────────────────── */
function TypeBadge({ type }) {
  return <span className={`rec-type-badge ${type}`}>{type}</span>;
}

/* ── Recommendations Panel ───────────────────────────────────────────────── */
function RecommendationsPanel({ recommendations = [] }) {
  if (!recommendations || recommendations.length === 0) return null;

  return (
    <div className="recs-section">
      <div className="recs-header">
        <span className="recs-icon">🎓</span>
        <span className="recs-title">Learning Resources for Missing Skills</span>
        <span className="recs-count">{recommendations.length} skills</span>
      </div>

      <div className="rec-list">
        {recommendations.map((rec) => (
          <div className="rec-item" key={rec.skill}>
            <div className="rec-skill-name">{rec.skill}</div>
            <div className="rec-resources">
              {(rec.resources || []).map((r, i) => (
                <a
                  key={i}
                  href={r.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rec-resource-link"
                  title={r.title}
                >
                  <TypeBadge type={r.type} />
                  <span className="rec-link-title">{r.title}</span>
                  {r.free && <span className="rec-free-tag">FREE</span>}
                </a>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── Result Card ─────────────────────────────────────────────────────────── */
function ResultCard({ result }) {
  if (!result) return null;

  const breakdown      = result?.similarity_breakdown ?? null;
  const resumeSkills   = result?.resume_skills        ?? [];
  const jobSkills      = result?.job_skills           ?? [];
  const matched        = result?.matched_skills       ?? [];
  const missing        = result?.missing_skills       ?? [];
  const recommendations = result?.recommendations     ?? [];

  return (
    <div className="card result-card">

      {/* ── Score Row ──────────────────────────────────────────────── */}
      <div className="result-score-row">
        <ScoreGauge value={result.match_percentage} />
      </div>

      {/* ── Stats ──────────────────────────────────────────────────── */}
      <div className="stats-row">
        <div className="stat">
          <div className="stat-value" style={{ color: "var(--blue)" }}>{jobSkills.length}</div>
          <div className="stat-label">JD Skills</div>
        </div>
        <div className="stat">
          <div className="stat-value" style={{ color: "var(--green)" }}>{matched.length}</div>
          <div className="stat-label">Matched</div>
        </div>
        <div className="stat">
          <div className="stat-value" style={{ color: "var(--red)" }}>{missing.length}</div>
          <div className="stat-label">Missing</div>
        </div>
        <div className="stat">
          <div className="stat-value">{resumeSkills.length}</div>
          <div className="stat-label">Resume Skills</div>
        </div>
      </div>

      {/* ── Similarity Breakdown ───────────────────────────────────── */}
      {breakdown && (
        <div className="metrics">
          <div className="metrics-title">Similarity Breakdown</div>
          <MetricBar label="Skill match score"  value={breakdown.skill_match_score} />
          <MetricBar label="Text similarity"    value={breakdown.text_similarity_score} />
        </div>
      )}

      {/* ── Learning Recommendations ───────────────────────────────── */}
      {missing.length > 0 && (
        <RecommendationsPanel recommendations={recommendations} />
      )}

      {/* ── Skill Grids ────────────────────────────────────────────── */}
      <div className="skills-section-title">Skill Breakdown</div>
      <div className="grid">
        <SkillList title="✅ Matched Skills"    skills={matched}      variant="matched" />
        <SkillList title="❌ Missing Skills"    skills={missing}      variant="missing" />
        <SkillList title="📋 JD Required"       skills={jobSkills}    variant="jd" />
        <SkillList title="📄 Your Resume"       skills={resumeSkills} variant="default" />
      </div>
    </div>
  );
}

export default ResultCard;