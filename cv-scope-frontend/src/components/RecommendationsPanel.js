import { useState } from "react";

function RecommendationCard({ rec }) {
  const [open, setOpen] = useState(false);

  return (
    <div className={`rec-card ${open ? "rec-open" : ""}`}>
      <div
        className="rec-header"
        onClick={() => setOpen(!open)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === "Enter" && setOpen(!open)}
      >
        <div className="rec-title-row">
          <span className="rec-skill-name">{rec.skill}</span>
          {rec.has_detailed_guide
            ? <span className="rec-badge guide">📘 Guide Available</span>
            : <span className="rec-badge generic">📄 Generic</span>}
        </div>
        <p className="rec-why">{rec.why_it_matters}</p>
        <span className="rec-toggle">{open ? "▲ Less" : "▼ More"}</span>
      </div>

      {open && (
        <div className="rec-body">
          {rec.prerequisites?.length > 0 && (
            <div className="rec-section">
              <div className="rec-section-title">🔑 Prerequisites</div>
              <div className="pill-list">
                {rec.prerequisites.map((p) => (
                  <span key={p} className="pill pill-purple">{p}</span>
                ))}
              </div>
            </div>
          )}

          {rec.learning_order?.length > 0 && (
            <div className="rec-section">
              <div className="rec-section-title">📋 Learning Order</div>
              <ol className="learning-list">
                {rec.learning_order.map((step, i) => (
                  <li key={i} className="learning-step">{step}</li>
                ))}
              </ol>
            </div>
          )}

          {rec.suggested_project && (
            <div className="rec-section">
              <div className="rec-section-title">🛠️ Practice Project</div>
              <div className="project-box">{rec.suggested_project}</div>
            </div>
          )}

          {rec.resources?.length > 0 && (
            <div className="rec-section">
              <div className="rec-section-title">🔗 Resources</div>
              <ul className="resource-list">
                {rec.resources.map((r) => (
                  <li key={r.url}>
                    <a href={r.url} target="_blank" rel="noopener noreferrer" className="resource-link">
                      {r.title} ↗
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function RecommendationsPanel({ result }) {
  const missing = result.missing_skills || [];
  const recs = result.skill_recommendations || [];

  if (missing.length === 0) {
    return (
      <div className="empty-state-small">
        <div style={{ fontSize: 48 }}>🎉</div>
        <h3>No Missing Skills!</h3>
        <p>Your resume covers all skills identified in the job description.</p>
      </div>
    );
  }

  return (
    <div className="recs-panel">
      <div className="recs-header">
        <h3 className="recs-title">Skill Gap Analysis</h3>
        <p className="recs-subtitle">
          {missing.length} skill{missing.length !== 1 ? "s" : ""} from the job description
          were not detected in your resume. Click each card to see a learning path.
        </p>
        <div className="recs-note">
          ⚠️ Absence from this list does not mean you lack these skills —
          the system only detects skills mentioned explicitly in your resume text.
        </div>
      </div>
      <div className="recs-list">
        {recs.map((rec) => (
          <RecommendationCard key={rec.skill} rec={rec} />
        ))}
      </div>
    </div>
  );
}

export default RecommendationsPanel;
