import { useState } from "react";

const CATEGORY_ICONS = {
  "Programming Languages": "💻",
  "Frontend Development": "🌐",
  "Backend Development": "⚙️",
  "Databases": "🗄️",
  "AI and Machine Learning": "🤖",
  "Data Analytics": "📊",
  "Cloud Computing": "☁️",
  "DevOps": "🚀",
  "Cybersecurity": "🔒",
  "Software Development": "🛠️",
  "Mobile Development": "📱",
  "Blockchain": "⛓️",
  "Tools": "🔧",
  "Other": "📦",
};

function SkillDetailCard({ detail }) {
  const [open, setOpen] = useState(false);
  const conf = Math.round((detail.confidence || 0) * 100);
  const confColor =
    conf >= 80 ? "#22c55e" : conf >= 50 ? "#f59e0b" : "#94a3b8";

  return (
    <div className="skill-detail-card">
      <div
        className="skill-detail-header"
        onClick={() => setOpen(!open)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === "Enter" && setOpen(!open)}
      >
        <div className="sdk-left">
          <span className="sdk-name">{detail.skill}</span>
          <div className="confidence-bar-wrap">
            <div
              className="confidence-bar"
              style={{ width: `${conf}%`, background: confColor }}
            />
          </div>
          <span className="conf-pct" style={{ color: confColor }}>{conf}%</span>
        </div>
        <span className="sdk-toggle">{open ? "▲" : "▼"}</span>
      </div>
      {open && (
        <div className="skill-detail-body">
          <div className="sdk-row">
            <span className="sdk-key">Sources:</span>
            <span>{detail.sources?.join(", ") || "—"}</span>
          </div>
          <div className="sdk-row">
            <span className="sdk-key">Sections:</span>
            <span>{detail.sections?.join(", ") || "—"}</span>
          </div>
          {detail.surface_forms?.length > 0 && (
            <div className="sdk-row">
              <span className="sdk-key">Found as:</span>
              <span>
                {detail.surface_forms.map((sf) => (
                  <code key={sf} className="surface-form">{sf}</code>
                ))}
              </span>
            </div>
          )}
          <div className="sdk-note">
            Confidence = base_confidence × section_weight × techiness_multiplier.
            Multi-source agreement adds a small boost (up to +0.05 per extra source).
          </div>
        </div>
      )}
    </div>
  );
}

function CategoryBlock({ category, skills }) {
  const icon = CATEGORY_ICONS[category] || "📦";
  return (
    <div className="category-block">
      <div className="cat-header">
        <span className="cat-icon">{icon}</span>
        <span className="cat-name">{category}</span>
        <span className="cat-count">{skills.length}</span>
      </div>
      <div className="pill-list">
        {skills.map((s) => (
          <span key={s} className="pill pill-blue">{s}</span>
        ))}
      </div>
    </div>
  );
}

function SkillsPanel({ result }) {
  const [view, setView] = useState("categories");
  const categories = result.skill_categories || {};
  const resumeDetails = result.resume_skill_details || [];
  const jdDetails = result.job_skill_details || [];
  const hasCats = Object.keys(categories).length > 0;

  return (
    <div className="skills-panel">
      <div className="view-toggle">
        <button
          className={`view-btn ${view === "categories" ? "active" : ""}`}
          onClick={() => setView("categories")}
        >🏷️ By Category</button>
        <button
          className={`view-btn ${view === "resume" ? "active" : ""}`}
          onClick={() => setView("resume")}
        >📄 Resume Skills</button>
        <button
          className={`view-btn ${view === "jd" ? "active" : ""}`}
          onClick={() => setView("jd")}
        >📌 JD Skills</button>
      </div>

      {view === "categories" && (
        <div className="category-grid">
          {hasCats
            ? Object.entries(categories).map(([cat, skills]) => (
                <CategoryBlock key={cat} category={cat} skills={skills} />
              ))
            : <p className="empty-msg">No categorised skills found.</p>}
        </div>
      )}

      {view === "resume" && (
        <div>
          <p className="section-note">
            Each skill shows its extraction confidence. Expand for evidence details.
          </p>
          {resumeDetails.length > 0
            ? resumeDetails.map((d) => <SkillDetailCard key={d.skill} detail={d} />)
            : <p className="empty-msg">No skills extracted from resume.</p>}
        </div>
      )}

      {view === "jd" && (
        <div>
          <p className="section-note">
            Skills identified in the job description.
          </p>
          {jdDetails.length > 0
            ? jdDetails.map((d) => <SkillDetailCard key={d.skill} detail={d} />)
            : <p className="empty-msg">No skills identified in job description.</p>}
        </div>
      )}
    </div>
  );
}

export default SkillsPanel;
