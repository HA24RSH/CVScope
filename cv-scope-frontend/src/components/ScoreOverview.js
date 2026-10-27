function clamp(v) {
  const n = Number(v);
  return Number.isFinite(n) ? Math.max(0, Math.min(100, n)) : 0;
}

function ScoreGauge({ value, size = 140 }) {
  const pct = clamp(value);
  const stroke = 11;
  const r = (size - stroke * 2) / 2;
  const cx = size / 2;
  const cy = size / 2;
  const circumference = 2 * Math.PI * r;
  const offset = circumference * (1 - pct / 100);

  const color =
    pct >= 75 ? "#22c55e" :
    pct >= 50 ? "#f59e0b" :
    "#ef4444";

  return (
    <div
      className="score-gauge"
      style={{ width: size, height: size }}
      aria-label={`Match score ${Math.round(pct)} percent`}
    >
      <svg viewBox={`0 0 ${size} ${size}`} style={{ width: size, height: size, transform: "rotate(-90deg)" }}>
        <circle className="gauge-track" cx={cx} cy={cy} r={r} strokeWidth={stroke} />
        <circle
          className="gauge-progress"
          cx={cx} cy={cy} r={r}
          strokeWidth={stroke}
          style={{ stroke: color, strokeDasharray: `${circumference} ${circumference}`, strokeDashoffset: offset }}
        />
      </svg>
      <div className="gauge-center">
        <div className="gauge-value" style={{ color }}>{Math.round(pct)}%</div>
        <div className="gauge-label">Match</div>
      </div>
    </div>
  );
}

function MetricBar({ label, value, color }) {
  const pct = clamp(value);
  return (
    <div className="metric-bar">
      <div className="metric-top">
        <span className="metric-label">{label}</span>
        <span className="metric-val">{pct.toFixed(1)}%</span>
      </div>
      <div className="metric-track">
        <div
          className="metric-fill"
          style={{ width: `${pct}%`, background: color || "var(--primary-grad)" }}
        />
      </div>
    </div>
  );
}

function StatCard({ label, value, icon, highlight }) {
  return (
    <div className={`stat-card ${highlight ? "stat-highlight" : ""}`}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-num">{value}</div>
      <div className="stat-lbl">{label}</div>
    </div>
  );
}

function ScoreOverview({ result }) {
  const bd = result.similarity_breakdown || {};
  const matched = result.matched_skills || [];
  const missing = result.missing_skills || [];
  const jdSkills = result.job_skills || [];
  const resumeSkills = result.resume_skills || [];
  const skillCovPct = jdSkills.length > 0 ? Math.round(matched.length / jdSkills.length * 100) : 0;

  return (
    <div className="overview-panel">
      {/* Score row */}
      <div className="score-row">
        <div className="score-left">
          <ScoreGauge value={result.match_percentage} size={150} />
          <div className="score-disclaimer">
            Keyword-based match. Does not predict hiring outcomes.
          </div>
        </div>
        <div className="score-right">
          <div className="metrics-card">
            <div className="metrics-heading">Score Breakdown</div>
            <MetricBar
              label="Skill Match"
              value={bd.skill_match_score}
              color="linear-gradient(90deg, #6366f1, #8b5cf6)"
            />
            <MetricBar
              label="Text Similarity (TF-IDF)"
              value={bd.text_similarity_score}
              color="linear-gradient(90deg, #0ea5e9, #38bdf8)"
            />
            <MetricBar
              label="Skill Coverage"
              value={skillCovPct}
              color="linear-gradient(90deg, #10b981, #34d399)"
            />
            {bd.formula && (
              <div className="formula-box">
                <span className="formula-label">Formula: </span>
                {bd.formula}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <StatCard icon="📋" label="Resume Skills" value={resumeSkills.length} />
        <StatCard icon="📌" label="JD Skills" value={jdSkills.length} />
        <StatCard icon="✅" label="Matched" value={matched.length} highlight={matched.length > 0} />
        <StatCard icon="❌" label="Missing" value={missing.length} />
      </div>

      {/* Quick skill lists */}
      <div className="quick-skills-grid">
        <div className="quick-skill-box matched-box">
          <div className="qsb-title">✅ Matched Skills</div>
          <div className="pill-list">
            {matched.length > 0
              ? matched.map((s) => <span key={s} className="pill pill-green">{s}</span>)
              : <span className="empty-msg">None matched</span>}
          </div>
        </div>
        <div className="quick-skill-box missing-box">
          <div className="qsb-title">❌ Missing Skills</div>
          <div className="pill-list">
            {missing.length > 0
              ? missing.map((s) => <span key={s} className="pill pill-red">{s}</span>)
              : <span className="empty-msg">None missing 🎉</span>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ScoreOverview;
