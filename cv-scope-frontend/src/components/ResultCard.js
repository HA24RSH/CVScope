import SkillList from "./SkillList";

function ResultCard({ result }) {
  if (!result) return null;

  return (
    <div className="card result-card">
      <h2>Match Score: {result.match_percentage}%</h2>

      <div className="grid">
        <SkillList title="Resume Skills" skills={result?.resume_skills || []} />
        <SkillList title="Job Skills" skills={result?.job_skills || []} />
        <SkillList title="Matched Skills" skills={result?.matched_skills || []} />
        <SkillList title="Missing Skills" skills={result?.missing_skills || []} />
      </div>
    </div>
  );
}

export default ResultCard;