/**
 * SkillList — renders a labelled pill-grid of skills.
 * variant: "default" | "matched" | "missing" | "jd"
 */
function SkillList({ title, skills = [], variant = "default" }) {
  const list = Array.isArray(skills) ? skills : [];

  return (
    <div className="skill-box">
      <div className="skill-box-header">
        <h3 className="skill-box-title">{title}</h3>
        <div className="skill-box-count">{list.length}</div>
      </div>

      {list.length > 0 ? (
        <ul className="skill-pills">
          {list.map((s, i) => (
            <li className={`pill ${variant}`} key={`${s}-${i}`}>
              {s}
            </li>
          ))}
        </ul>
      ) : (
        <p className="empty-pill-msg">None</p>
      )}
    </div>
  );
}

export default SkillList;