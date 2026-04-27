function Header() {
  return (
    <header className="app-header">
      <div className="header-inner">
        {/* Left: gold dot + wordmark */}
        <div className="brand-logo">
          <div className="brand-dot" aria-hidden="true" />
          <div className="brand-title">CVScope</div>
        </div>

        {/* Right: status pill */}
        <div className="header-pill" role="status" aria-label="NLP v2 Live">
          <span className="header-pill-dot" aria-hidden="true" />
          NLP v2 · Live
        </div>
      </div>
    </header>
  );
}

export default Header;