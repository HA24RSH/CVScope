import SkillList from "./SkillList";

function clampPct(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return 0;
  return Math.max(0, Math.min(100, n));
}

function ScoreGauge({ value }) {
  const pct = clampPct(value);
  const stroke = 10;
  const r = 50;
  const circumference = 2 * Math.PI * r;
  const offset = circumference * (1 - pct / 100);

  return (
    <div className="score-gauge" aria-label={`Match score ${Math.round(pct)} percent`}>
      <svg viewBox="0 0 120 120" role="img">
        <circle
          className="score-gauge-track"
          cx="60"
          cy="60"
          r={r}
          strokeWidth={stroke}
        />
        <circle
          className="score-gauge-progress"
          cx="60"
          cy="60"
          r={r}
          strokeWidth={stroke}
          strokeDasharray={`${circumference} ${circumference}`}
          strokeDashoffset={offset}
        />
      </svg>

      <div className="score-gauge-center">
        <div className="score-gauge-value">{Math.round(pct)}%</div>
        <div className="score-gauge-label">Match</div>
      </div>
    </div>
  );
}

function MetricBar({ label, value }) {
  const pct = clampPct(value);
  return (
    <div className="metric">
      <div className="metric-top">
        <div className="metric-label">{label}</div>
        <div className="metric-value">{pct.toFixed(2)}%</div>
      </div>
      <div className="metric-track" aria-hidden="true">
        <div className="metric-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="stat">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

function ResultCard({ result }) {
  if (!result) return null;

  const breakdown = result?.similarity_breakdown || null;
  const resumeSkills = result?.resume_skills || [];
  const jobSkills = result?.job_skills || [];
  const matched = result?.matched_skills || [];
  const missing = result?.missing_skills || [];

  return (
    <div className="card result-card">
      <div className="result-score-row">
        <h2>Match Score</h2>
        <ScoreGauge value={result.match_percentage} />
      </div>

      <div className="stats-row">
        <Stat label="JD skills" value={jobSkills.length} />
        <Stat label="Matched" value={matched.length} />
        <Stat label="Missing" value={missing.length} />
        <Stat label="Resume skills" value={resumeSkills.length} />
      </div>

      {breakdown ? (
        <div className="metrics">
          <div className="metrics-title">Similarity breakdown</div>
          <MetricBar label="Skill match" value={breakdown.skill_match_score} />
          <MetricBar label="Text similarity" value={breakdown.text_similarity_score} />
        </div>
      ) : null}

      <div className="grid">
        <SkillList title="Resume Skills" skills={resumeSkills} />
        <SkillList title="Job Skills" skills={jobSkills} />
        <SkillList title="Matched Skills" skills={matched} />
        <SkillList title="Missing Skills" skills={missing} />
      </div>
    </div>
  );
}

export default ResultCard;