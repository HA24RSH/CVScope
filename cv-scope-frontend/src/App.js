import { useState } from "react";
import Header from "./components/Header";
import UploadForm from "./components/UploadForm";
import ResultCard from "./components/ResultCard";
import "./styles/global.css";

function EmptyState() {
  return (
    <div className="card empty-state">
      <div className="empty-illustration">🎯</div>
      <h2 className="empty-title">Your results will appear here</h2>
      <p className="empty-subtitle">
        Upload a resume and paste a job description to see your match score,
        skill gaps, and personalized learning resources.
      </p>
      <div className="empty-hints">
        <div className="hint">
          <span className="hint-icon">📄</span>
          PDF or DOCX resume supported
        </div>
        <div className="hint">
          <span className="hint-icon">🧠</span>
          4-layer NLP pipeline extracts skills
        </div>
        <div className="hint">
          <span className="hint-icon">✅</span>
          Matched &amp; missing skills highlighted
        </div>
        <div className="hint">
          <span className="hint-icon">🎓</span>
          Free learning resources for skill gaps
        </div>
      </div>
    </div>
  );
}

function App() {
  const [result, setResult] = useState(null);

  return (
    <div className="container">
      <Header />

      <main className="layout">
        <section className="panel">
          <div className="panel-title">Analyze</div>
          <UploadForm onResult={setResult} />
        </section>

        <section className="panel">
          <div className="panel-title">Dashboard</div>
          {result ? <ResultCard result={result} /> : <EmptyState />}
        </section>
      </main>
    </div>
  );
}

export default App;