function SkillList({ title, skills = [] }) {
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
            <li className="pill" key={`${s}-${i}`}>
              {s}
            </li>
          ))}
        </ul>
      ) : (
        <p className="empty">None</p>
      )}
    </div>
  );
}

export default SkillList;