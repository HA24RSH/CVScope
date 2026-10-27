function Header() {
  return (
    <header className="app-header">
      <div className="brand">
        <div className="brand-logo">
          <span className="logo-icon">🔍</span>
          <span className="brand-name">CVScope</span>
        </div>
        <div className="brand-tagline">AI Resume Analysis &amp; Skill Matching</div>
      </div>
      <div className="header-badges">
        <span className="badge badge-ai">NLP v3</span>
        <span className="badge badge-local">100% Local</span>
        <span className="badge badge-free">Free</span>
      </div>
    </header>
  );
}

export default Header;