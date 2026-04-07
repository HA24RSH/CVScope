import { useState } from "react";
import Header from "./components/Header";
import UploadForm from "./components/UploadForm";
import ResultCard from "./components/ResultCard";
import "./styles/global.css";

function EmptyState() {
  return (
    <div className="card empty-state">
      <h2 className="empty-title">Results</h2>
      <p className="empty-subtitle">
        Upload a resume and paste a job description to see your match.
      </p>
      <div className="empty-hints">
        <div className="hint">PDF or DOCX supported</div>
        <div className="hint">Shows matched and missing skills</div>
        <div className="hint">Breaks down skills vs text similarity</div>
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