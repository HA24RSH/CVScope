function ExplainPanel({ result }) {
  const explanations = result.score_explanation || [];
  const bd = result.similarity_breakdown || {};

  const concepts = [
    {
      icon: "📐",
      title: "TF-IDF Cosine Similarity",
      body: "TF-IDF (Term Frequency–Inverse Document Frequency) converts text into a numerical vector where each dimension represents a word's importance. Words that appear frequently in a document but rarely across all documents get a higher weight. Cosine similarity then measures the angle between two vectors — a score of 1 means identical, 0 means completely different. CVScope applies TF-IDF separately to the Skills section, Experience section, and full document, then combines them with weights (50%/30%/20%).",
    },
    {
      icon: "🔤",
      title: "Lexical vs Semantic Similarity",
      body: "TF-IDF is a lexical method — it compares exact word occurrences. If your resume says 'Node.js' and the JD says 'NodeJS', they may not match unless an alias is defined. Semantic methods (like word embeddings) understand that 'automobile' and 'car' mean the same thing. CVScope addresses this gap through its alias taxonomy (220+ skill aliases) and RapidFuzz fuzzy matching, rather than large pretrained models. This keeps the system lightweight and fully local.",
    },
    {
      icon: "🔍",
      title: "PhraseMatcher (spaCy)",
      body: "CVScope uses spaCy's PhraseMatcher to scan text for known skill phrases. Every alias in the taxonomy (e.g. 'ReactJS', 'react.js', 'React JS') is registered as a pattern. When any alias is found, it is mapped to its canonical name (e.g. 'react'). This is the highest-confidence extraction method because matches are exact (case-insensitive).",
    },
    {
      icon: "🤖",
      title: "NER as Fallback",
      body: "spaCy's Named Entity Recognition (NER) identifies ORG and PRODUCT entities — categories that often contain technology names. This catches newer or unusual technologies not in the taxonomy. However, NER also picks up company names (e.g. 'Google') and non-technical products, so CVScope applies strict noise filtering and lower confidence scores (0.5–0.82 vs 0.95 for taxonomy matches).",
    },
    {
      icon: "📊",
      title: "Confidence Score Formula",
      body: "confidence = base_confidence × section_weight × techiness_multiplier, clamped to [0, 1]. base_confidence: 0.95 (taxonomy match), 0.82 (NER normalized), 0.65 (NER product), 0.55 (noun chunk), 0.60 (YAKE keyword). section_weight: Skills=1.0, Projects=0.85, Experience=0.75, Education=0.45, Other=0.35. techiness_multiplier: boosted for acronyms (+25%), tech punctuation (+15%), penalised for vague multi-word phrases (×0.75). Multi-source agreement adds up to +0.05.",
    },
    {
      icon: "⚖️",
      title: "Final Score Formula",
      body: "final_score = 0.60 × skill_match_score + 0.40 × text_similarity_score. skill_match_score = (sum of confidence weights of matched JD skills) / (sum of confidence weights of all JD skills) × 100. The 60/40 split reflects that keyword presence is more directly measurable than text similarity, while text similarity captures context that pure skill lists miss.",
    },
  ];

  return (
    <div className="explain-panel">
      {/* Actual explanation from backend */}
      {explanations.length > 0 && (
        <div className="explain-section">
          <h3 className="explain-heading">📋 Your Score Explained</h3>
          <div className="explanation-list">
            {explanations.map((line, i) => (
              <div key={i} className="explanation-item">
                <span className="exp-bullet">→</span>
                <span>{line}</span>
              </div>
            ))}
          </div>
          {bd.formula && (
            <div className="formula-display">
              <span className="formula-key">Formula used: </span>
              {bd.formula}
            </div>
          )}
        </div>
      )}

      {/* AI/NLP concepts */}
      <div className="explain-section">
        <h3 className="explain-heading">🎓 AI Concepts Behind This Project</h3>
        <div className="concept-list">
          {concepts.map((c) => (
            <div key={c.title} className="concept-card">
              <div className="concept-icon">{c.icon}</div>
              <div className="concept-body">
                <div className="concept-title">{c.title}</div>
                <p className="concept-text">{c.body}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="explain-disclaimer">
        <strong>Academic Note:</strong> CVScope is an NLP project that demonstrates practical
        applications of text similarity, information extraction, and rule-based recommendation.
        All processing is local and no external AI APIs are used. The system is designed to be
        transparent, reproducible, and understandable at the source-code level.
      </div>
    </div>
  );
}

export default ExplainPanel;
