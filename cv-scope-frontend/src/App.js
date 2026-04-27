import { useState, useRef } from "react";
import Header from "./components/Header";
import UploadForm from "./components/UploadForm";
import ResultCard from "./components/ResultCard";
import "./styles/global.css";

/* ── Empty State ─────────────────────────────────────────────────────────── */
function EmptyState() {
  return (
    <div className="empty-state">
      <div className="empty-dot">
        <div className="empty-dot-inner" aria-hidden="true" />
      </div>
      <p className="empty-title">Your analysis will appear here</p>
      <p className="empty-subtitle">
        Upload a resume and paste a job description, then click Analyze Match.
      </p>
    </div>
  );
}

/* ── App ─────────────────────────────────────────────────────────────────── */
function App() {
  const [result, setResult] = useState(null);
  const dashboardRef = useRef(null);

  return (
    <div>
      <Header />

      <div className="container page-body">
        <div className="layout">

          {/* ── Analyze Section ───────────────────────────────────────── */}
          <section className="panel" aria-label="Analyze">
            <div className="section-label">Analyze</div>
            <UploadForm onResult={setResult} dashboardRef={dashboardRef} />
          </section>

          {/* ── Dashboard Section ─────────────────────────────────────── */}
          <section
            className="panel"
            aria-label="Dashboard"
            ref={dashboardRef}
          >
            <div className="section-label">Dashboard</div>
            {result ? <ResultCard result={result} /> : <EmptyState />}
          </section>

        </div>
      </div>
    </div>
  );
}

export default App;