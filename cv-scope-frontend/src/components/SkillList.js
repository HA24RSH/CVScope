function SkillList({ title, skills }) {
  return (
    <div className="skill-box">
      <h3>{title}</h3>
      {skills.length === 0 ? (
        <p className="empty">None</p>
      ) : (
        <ul>
          {skills.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default SkillList;