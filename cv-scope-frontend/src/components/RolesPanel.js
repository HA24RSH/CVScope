import { useState } from "react";

function RoleBar({ value, color }) {
  const pct = Math.max(0, Math.min(100, Number(value) || 0));
  return (
    <div className="role-bar-track">
      <div
        className="role-bar-fill"
        style={{ width: `${pct}%`, background: color }}
      />
      <span className="role-bar-label">{pct.toFixed(0)}%</span>
    </div>
  );
}

function RoleCard({ role, rank }) {
  const [open, setOpen] = useState(false);
  const score = role.overall_score || 0;

  const scoreColor =
    score >= 70 ? "#22c55e" :
    score >= 40 ? "#f59e0b" :
    "#94a3b8";

  return (
    <div className={`role-card ${rank === 0 ? "role-top" : ""}`}>
      {rank === 0 && <div className="role-top-badge">🏆 Best Match</div>}
      <div
        className="role-card-header"
        onClick={() => setOpen(!open)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === "Enter" && setOpen(!open)}
      >
        <div className="role-icon">{role.icon || "💼"}</div>
        <div className="role-info">
          <div className="role-name">{role.role}</div>
          <div className="role-desc">{role.description}</div>
        </div>
        <div className="role-score" style={{ color: scoreColor }}>
          {score.toFixed(0)}%
          <div className="role-score-label">Overall</div>
        </div>
        <span className="role-toggle">{open ? "▲" : "▼"}</span>
      </div>

      <div className="role-bars">
        <div className="role-bar-row">
          <span className="role-bar-key">Required</span>
          <RoleBar value={role.required_coverage} color="linear-gradient(90deg, #6366f1, #8b5cf6)" />
        </div>
        <div className="role-bar-row">
          <span className="role-bar-key">Preferred</span>
          <RoleBar value={role.preferred_coverage} color="linear-gradient(90deg, #0ea5e9, #38bdf8)" />
        </div>
      </div>

      {open && (
        <div className="role-detail">
          {role.matched_required?.length > 0 && (
            <div className="role-skill-group">
              <div className="rsg-title">✅ Required — Found</div>
              <div className="pill-list">
                {role.matched_required.map((s) => (
                  <span key={s} className="pill pill-green">{s}</span>
                ))}
              </div>
            </div>
          )}
          {role.missing_required?.length > 0 && (
            <div className="role-skill-group">
              <div className="rsg-title">❌ Required — Missing</div>
              <div className="pill-list">
                {role.missing_required.map((s) => (
                  <span key={s} className="pill pill-red">{s}</span>
                ))}
              </div>
            </div>
          )}
          {role.matched_preferred?.length > 0 && (
            <div className="role-skill-group">
              <div className="rsg-title">✅ Preferred — Found</div>
              <div className="pill-list">
                {role.matched_preferred.map((s) => (
                  <span key={s} className="pill pill-blue">{s}</span>
                ))}
              </div>
            </div>
          )}
          {role.missing_preferred?.length > 0 && (
            <div className="role-skill-group">
              <div className="rsg-title">○ Preferred — Missing</div>
              <div className="pill-list">
                {role.missing_preferred.map((s) => (
                  <span key={s} className="pill pill-grey">{s}</span>
                ))}
              </div>
            </div>
          )}
          {role.related_roles?.length > 0 && (
            <div className="role-related">
              Related roles: {role.related_roles.join(" · ")}
            </div>
          )}
          <div className="role-disclaimer">
            Scores reflect skill keyword overlap with the role profile.
            They do not predict interview outcomes or employability.
          </div>
        </div>
      )}
    </div>
  );
}

function RolesPanel({ result }) {
  const roles = result.role_matches || [];

  if (roles.length === 0) {
    return (
      <div className="empty-state-small">
        <div style={{ fontSize: 48 }}>💼</div>
        <h3>No Role Data</h3>
        <p>Role recommendations require at least some skills to be extracted from your resume.</p>
      </div>
    );
  }

  return (
    <div className="roles-panel">
      <div className="roles-header">
        <h3 className="roles-title">Job Role Recommendations</h3>
        <p className="roles-subtitle">
          Your resume was compared against {roles.length} predefined job role profiles.
          Results are ranked by skill coverage (70% required + 30% preferred).
        </p>
      </div>
      <div className="roles-list">
        {roles.map((role, i) => (
          <RoleCard key={role.role} role={role} rank={i} />
        ))}
      </div>
    </div>
  );
}

export default RolesPanel;
