function Header() {
  return (
    <header className="app-header">
      <div className="brand">
        <div className="brand-logo">
          <div className="brand-icon">🎯</div>
          <div className="brand-title">CVScope</div>
        </div>
        <div className="brand-subtitle">AI-powered resume analysis &amp; job matching</div>
      </div>

      <div className="header-right">
        <div className="brand-badge">
          <span className="badge-dot" />
          NLP v2 · Live
        </div>
      </div>
    </header>
  );
}

export default Header;