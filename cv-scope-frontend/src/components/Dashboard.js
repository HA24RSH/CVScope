import { useState } from "react";
import ScoreOverview from "./ScoreOverview";
import SkillsPanel from "./SkillsPanel";
import RecommendationsPanel from "./RecommendationsPanel";
import RolesPanel from "./RolesPanel";
import ExplainPanel from "./ExplainPanel";

const TABS = [
  { id: "overview", label: "Overview", icon: "📊" },
  { id: "skills", label: "Skills", icon: "🔧" },
  { id: "gap", label: "Skill Gap", icon: "📚" },
  { id: "roles", label: "Role Match", icon: "🎯" },
  { id: "explain", label: "Explainability", icon: "🔍" },
];

function EmptyState() {
  return (
    <div className="empty-state">
      <div className="empty-icon">📊</div>
      <h2 className="empty-title">Ready to Analyze</h2>
      <p className="empty-subtitle">
        Upload your resume and paste a job description to get your match score, skill gap analysis,
        and job role recommendations.
      </p>
      <div className="feature-grid">
        {[
          { icon: "🎯", title: "Skill Matching", desc: "Exact & fuzzy match across 220+ skills" },
          { icon: "📐", title: "TF-IDF Similarity", desc: "Section-weighted text similarity score" },
          { icon: "📚", title: "Skill Gap", desc: "Learning paths for missing skills" },
          { icon: "💼", title: "Role Matching", desc: "Match against 12 predefined job roles" },
          { icon: "🔍", title: "Explainability", desc: "Transparent scoring breakdown" },
          { icon: "🏷️", title: "Categorisation", desc: "Skills grouped by domain" },
        ].map((f) => (
          <div className="feature-card" key={f.title}>
            <span className="feature-icon">{f.icon}</span>
            <div className="feature-title">{f.title}</div>
            <div className="feature-desc">{f.desc}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="empty-state">
      <div className="loading-pulse">⚙️</div>
      <h2 className="empty-title">Analyzing…</h2>
      <p className="empty-subtitle">Running NLP pipeline on your resume</p>
    </div>
  );
}

function Dashboard({ result, isLoading }) {
  const [activeTab, setActiveTab] = useState("overview");

  if (isLoading) return <LoadingState />;
  if (!result) return <EmptyState />;

  return (
    <div className="dashboard">
      {/* Tab navigation */}
      <nav className="tabs" role="tablist" aria-label="Result sections">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeTab === tab.id}
            className={`tab-btn ${activeTab === tab.id ? "active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
            id={`tab-${tab.id}`}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
            {tab.id === "gap" && result.missing_skills?.length > 0 && (
              <span className="tab-badge">{result.missing_skills.length}</span>
            )}
          </button>
        ))}
      </nav>

      {/* Tab content */}
      <div className="tab-content" role="tabpanel" aria-labelledby={`tab-${activeTab}`}>
        {activeTab === "overview" && <ScoreOverview result={result} />}
        {activeTab === "skills" && <SkillsPanel result={result} />}
        {activeTab === "gap" && <RecommendationsPanel result={result} />}
        {activeTab === "roles" && <RolesPanel result={result} />}
        {activeTab === "explain" && <ExplainPanel result={result} />}
      </div>
    </div>
  );
}

export default Dashboard;
