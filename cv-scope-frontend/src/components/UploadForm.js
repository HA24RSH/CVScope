import { useState } from "react";

function LoadingBar({ label = "Analyzing…" }) {
  return (
    <div className="loading-wrap" aria-live="polite">
      <div className="loading-label">{label}</div>
      <div className="loading-bar" role="progressbar" aria-label={label} />
    </div>
  );
}

function UploadForm({ onResult }) {
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const apiBaseUrl = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";

  const handleSubmit = async () => {
    if (loading) return;
    setError("");

    if (!file || !jd.trim()) {
      setError("Upload a resume (PDF/DOCX) and paste a job description.");
      return;
    }

    setLoading(true);
    onResult(null);

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("job_description", jd);

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
        const message = data?.detail || `Request failed (${res.status})`;
        throw new Error(message);
      }

      // ✅ Safe fallback (prevents frontend crash)
      onResult({
        match_percentage: data.match_percentage ?? 0,
        resume_skills: data.resume_skills ?? [],
        job_skills: data.job_skills ?? [],
        matched_skills: data.matched_skills ?? [],
        missing_skills: data.missing_skills ?? [],
        similarity_breakdown: data.similarity_breakdown ?? null,
        resume_skill_details: data.resume_skill_details ?? [],
        job_skill_details: data.job_skill_details ?? [],
      });

    } catch (error) {
      console.error("Error:", error);
      setError(error?.message || "Failed to connect to backend");
    }

    setLoading(false);
  };

  return (
    <div className="card" aria-busy={loading}>
      <div className="field">
        <label className="label">Resume (PDF/DOCX)</label>
        <label className={`file-input ${loading ? "is-disabled" : ""}`}>
          <input
            type="file"
            accept=".pdf,.docx"
            disabled={loading}
            onChange={(e) => setFile(e.target.files[0] || null)}
          />
          <span className="file-button">Choose file</span>
          <span className="file-name">{file?.name || "No file selected"}</span>
        </label>
        <div className="help-text">Supported formats: PDF, DOCX</div>
      </div>

      <div className="field">
        <label className="label">Job description</label>
        <textarea
          disabled={loading}
          placeholder="Paste the job description here…"
          value={jd}
          onChange={(e) => setJd(e.target.value)}
          rows={7}
        />
      </div>

      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Analyzing..." : "Analyze"}
      </button>

      {loading && <LoadingBar label="Extracting skills & matching…" />}

      {error ? <div className="alert">{error}</div> : null}
    </div>
  );
}

export default UploadForm;