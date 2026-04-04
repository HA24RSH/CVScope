function SkillList({ title, skills = [] }) {
  return (
    <div className="skill-box">
      <h3>{title}</h3>

      {skills && skills.length > 0 ? (
        <ul>
          {skills.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ul>
      ) : (
        <p className="empty">None</p>
      )}
    </div>
  );
}

export default SkillList;