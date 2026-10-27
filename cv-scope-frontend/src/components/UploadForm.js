import { useState } from "react";

function LoadingSteps({ step }) {
  const steps = [
    "Extracting resume text…",
    "Identifying skills…",
    "Matching job requirements…",
    "Calculating similarity…",
    "Generating recommendations…",
  ];
  return (
    <div className="loading-steps" aria-live="polite">
      {steps.map((s, i) => (
        <div
          key={i}
          className={`loading-step ${i < step ? "done" : i === step ? "active" : "pending"}`}
        >
          <span className="step-dot">{i < step ? "✓" : i === step ? "●" : "○"}</span>
          <span>{s}</span>
        </div>
      ))}
    </div>
  );
}

function UploadForm({ onResult, onLoading }) {
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadStep, setLoadStep] = useState(0);
  const [error, setError] = useState("");
  const [dragOver, setDragOver] = useState(false);

  const apiBaseUrl = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";

  const handleFile = (f) => {
    if (!f) return;
    const ext = f.name.toLowerCase().split(".").pop();
    if (!["pdf", "docx"].includes(ext)) {
      setError("Only PDF and DOCX files are supported.");
      return;
    }
    setError("");
    setFile(f);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files[0]);
  };

  const simulateSteps = async () => {
    for (let i = 0; i < 5; i++) {
      setLoadStep(i);
      await new Promise((r) => setTimeout(r, 420));
    }
  };

  const handleSubmit = async () => {
    if (loading) return;
    setError("");

    if (!file) {
      setError("Please upload a resume (PDF or DOCX).");
      return;
    }
    if (!jd.trim()) {
      setError("Please paste a job description.");
      return;
    }
    if (jd.trim().length < 30) {
      setError("Job description is too short. Please provide at least a few sentences.");
      return;
    }

    setLoading(true);
    setLoadStep(0);
    onLoading(true);
    onResult(null);

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("job_description", jd);

    // Run step animation in parallel with fetch
    simulateSteps();

    try {
      const res = await fetch(`${apiBaseUrl}/analyze`, {
        method: "POST",
        body: formData,
      });

      let data = {};
      try {
        data = await res.json();
      } catch {
        data = {};
      }

      if (!res.ok) {
        throw new Error(data?.detail || `Request failed (${res.status})`);
      }

      onResult({
        match_percentage: data.match_percentage ?? 0,
        resume_skills: data.resume_skills ?? [],
        job_skills: data.job_skills ?? [],
        matched_skills: data.matched_skills ?? [],
        missing_skills: data.missing_skills ?? [],
        similarity_breakdown: data.similarity_breakdown ?? null,
        resume_skill_details: data.resume_skill_details ?? [],
        job_skill_details: data.job_skill_details ?? [],
        skill_categories: data.skill_categories ?? {},
        score_explanation: data.score_explanation ?? [],
        skill_recommendations: data.skill_recommendations ?? [],
        role_matches: data.role_matches ?? [],
      });
    } catch (err) {
      console.error("Analysis error:", err);
      setError(err?.message || "Failed to connect to backend. Is the server running?");
    } finally {
      setLoading(false);
      onLoading(false);
    }
  };

  return (
    <div className="card upload-card" aria-busy={loading}>
      <div className="card-title">
        <span className="card-icon">📄</span>
        Analyze Resume
      </div>

      {/* File drop zone */}
      <div
        className={`drop-zone ${dragOver ? "drag-over" : ""} ${file ? "has-file" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => document.getElementById("file-input-hidden").click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === "Enter" && document.getElementById("file-input-hidden").click()}
        aria-label="Upload resume file"
      >
        <input
          id="file-input-hidden"
          type="file"
          accept=".pdf,.docx"
          style={{ display: "none" }}
          disabled={loading}
          onChange={(e) => handleFile(e.target.files[0])}
        />
        {file ? (
          <div className="drop-zone-selected">
            <span className="file-icon">📋</span>
            <div>
              <div className="file-name-display">{file.name}</div>
              <div className="file-size">{(file.size / 1024).toFixed(1)} KB</div>
            </div>
            <button
              className="remove-file"
              onClick={(e) => { e.stopPropagation(); setFile(null); }}
              title="Remove file"
            >×</button>
          </div>
        ) : (
          <div className="drop-zone-prompt">
            <div className="drop-icon">☁</div>
            <div className="drop-label">Drop PDF or DOCX here</div>
            <div className="drop-sublabel">or click to browse</div>
          </div>
        )}
      </div>

      {/* Job description */}
      <div className="field">
        <label className="field-label" htmlFor="jd-textarea">Job Description</label>
        <textarea
          id="jd-textarea"
          disabled={loading}
          placeholder="Paste the full job description here…"
          value={jd}
          onChange={(e) => setJd(e.target.value)}
          rows={8}
        />
        {jd.trim().length > 0 && (
          <div className="char-count">{jd.trim().split(/\s+/).length} words</div>
        )}
      </div>

      <button
        className="btn-analyze"
        onClick={handleSubmit}
        disabled={loading || !file || !jd.trim()}
        id="analyze-button"
      >
        {loading ? (
          <><span className="spinner" />Analyzing…</>
        ) : (
          <>⚡ Analyze Match</>
        )}
      </button>

      {loading && <LoadingSteps step={loadStep} />}

      {error && (
        <div className="alert-error" role="alert">
          ⚠ {error}
        </div>
      )}
    </div>
  );
}

export default UploadForm;