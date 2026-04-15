import { useState, useRef } from "react";

const STEPS = [
  "Extracting text from resume…",
  "Running NLP skill pipeline…",
  "Matching skills against JD…",
  "Calculating match score…",
];

function LoadingSteps({ activeStep }) {
  return (
    <div className="loading-wrap">
      <div className="loading-steps">
        {STEPS.map((label, i) => {
          const isDone   = i < activeStep;
          const isActive = i === activeStep;
          return (
            <div
              key={i}
              className={`loading-step${isDone ? " done" : isActive ? " active" : ""}`}
            >
              <span className="step-dot" />
              {isDone ? "✓ " : ""}{label}
            </div>
          );
        })}
      </div>
      <div style={{ marginTop: 10 }}>
        <div className="loading-bar-track">
          <div className="loading-bar-fill" />
        </div>
      </div>
    </div>
  );
}

function UploadForm({ onResult }) {
  const [file, setFile]         = useState(null);
  const [jd, setJd]             = useState("");
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");
  const [dragOver, setDragOver] = useState(false);
  const [step, setStep]         = useState(0);
  const dropRef                 = useRef(null);

  const apiBaseUrl = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";
  const JD_MAX = 8000;

  /* ── Drag & drop handlers ─────────────────────────────────────────── */
  const handleDragOver = (e) => { e.preventDefault(); setDragOver(true); };
  const handleDragLeave = ()  => setDragOver(false);
  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) pickFile(dropped);
  };

  const pickFile = (f) => {
    const ext = f.name.split(".").pop().toLowerCase();
    if (!["pdf", "docx"].includes(ext)) {
      setError("Only PDF and DOCX files are supported.");
      return;
    }
    setError("");
    setFile(f);
  };

  /* ── Submit ───────────────────────────────────────────────────────── */
  const handleSubmit = async () => {
    if (loading) return;
    setError("");

    if (!file || !jd.trim()) {
      setError("Upload a resume (PDF/DOCX) and paste a job description.");
      return;
    }

    setLoading(true);
    setStep(0);
    onResult(null);

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("job_description", jd);

    // Animate through loading steps
    const stepTimer = setInterval(() => {
      setStep((s) => (s < STEPS.length - 1 ? s + 1 : s));
    }, 900);

    try {
      const res = await fetch(`${apiBaseUrl}/analyze`, {
        method: "POST",
        body: formData,
      });

      clearInterval(stepTimer);
      setStep(STEPS.length);

      let data = {};
      try { data = await res.json(); } catch { data = {}; }

      if (!res.ok) {
        const message = data?.detail || `Request failed (${res.status})`;
        throw new Error(message);
      }

      onResult({
        match_percentage:     data.match_percentage      ?? 0,
        resume_skills:        data.resume_skills         ?? [],
        job_skills:           data.job_skills            ?? [],
        matched_skills:       data.matched_skills        ?? [],
        missing_skills:       data.missing_skills        ?? [],
        similarity_breakdown: data.similarity_breakdown  ?? null,
        resume_skill_details: data.resume_skill_details  ?? [],
        job_skill_details:    data.job_skill_details     ?? [],
        recommendations:      data.recommendations       ?? [],
      });
    } catch (err) {
      clearInterval(stepTimer);
      console.error("Error:", err);
      setError(err?.message || "Failed to connect to backend");
    }

    setLoading(false);
    setStep(0);
  };

  /* ── Render ───────────────────────────────────────────────────────── */
  return (
    <div className="card" aria-busy={loading}>

      {/* ── File Upload ──────────────────────────────────────────── */}
      <div className="field">
        <label className="label">Resume</label>
        <div
          ref={dropRef}
          className={`drop-zone${dragOver ? " drag-over" : ""}${file ? " has-file" : ""}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            type="file"
            accept=".pdf,.docx"
            disabled={loading}
            onChange={(e) => pickFile(e.target.files[0])}
          />
          <div className="drop-zone-inner">
            {file ? (
              <>
                <div className="drop-icon">✅</div>
                <div className="drop-filename">
                  <span>📄</span> {file.name}
                </div>
                <div className="drop-subtitle">
                  {(file.size / 1024).toFixed(1)} KB · Click to replace
                </div>
              </>
            ) : (
              <>
                <div className="drop-icon">📂</div>
                <div className="drop-title">
                  {dragOver ? "Drop it!" : "Drop your resume here"}
                </div>
                <div className="drop-subtitle">or click to browse · PDF or DOCX</div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* ── Job Description ──────────────────────────────────────── */}
      <div className="field">
        <label className="label">Job Description</label>
        <div className="textarea-wrap">
          <textarea
            disabled={loading}
            placeholder="Paste the full job description here…"
            value={jd}
            maxLength={JD_MAX}
            onChange={(e) => setJd(e.target.value)}
            rows={8}
          />
          <span className="char-counter">{jd.length}/{JD_MAX}</span>
        </div>
        <div className="help-text">Tip: include the full requirements section for best results</div>
      </div>

      {/* ── Submit Button ─────────────────────────────────────────── */}
      <button
        className="btn-analyze"
        onClick={handleSubmit}
        disabled={loading}
        id="analyze-btn"
      >
        {loading ? "Analyzing…" : "⚡ Analyze Match"}
      </button>

      {/* ── Loading Steps ─────────────────────────────────────────── */}
      {loading && <LoadingSteps activeStep={step} />}

      {/* ── Error ─────────────────────────────────────────────────── */}
      {error && (
        <div className="alert" role="alert">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}

export default UploadForm;