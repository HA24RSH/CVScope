import { useState } from "react";

function UploadForm({ onResult }) {
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!file || !jd) {
      alert("Please upload resume and enter job description");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("job_description", jd);

    try {
      const res = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      // ✅ Safe fallback (prevents frontend crash)
      onResult({
        match_percentage: data.match_percentage || 0,
        resume_skills: data.resume_skills || [],
        job_skills: data.job_skills || [],
        matched_skills: data.matched_skills || [],
        missing_skills: data.missing_skills || [],
      });

    } catch (error) {
      console.error("Error:", error);
      alert("Failed to connect to backend");

      // fallback empty state
      onResult({
        match_percentage: 0,
        resume_skills: [],
        job_skills: [],
        matched_skills: [],
        missing_skills: [],
      });
    }

    setLoading(false);
  };

  return (
    <div className="card">
      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <textarea
        placeholder="Paste Job Description..."
        value={jd}
        onChange={(e) => setJd(e.target.value)}
        rows={6}
      />

      <button onClick={handleSubmit}>
        {loading ? "Analyzing..." : "Analyze"}
      </button>
    </div>
  );
}

export default UploadForm;