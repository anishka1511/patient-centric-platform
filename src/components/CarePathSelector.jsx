import '../styles/CarePathSelector.css';

export default function CarePathSelector({ onSelectPath }) {
  return (
    <section className="care-path-selector">
      <div className="care-path-content">
        <h1 className="care-path-title">Healthcare Decision AI</h1>
        <p className="care-path-subtitle">Choose how you want to get recommendations</p>

        <div className="care-path-grid">
          <button
            type="button"
            className="care-path-card"
            onClick={() => onSelectPath('known')}
          >
            <span className="care-path-badge">Known input</span>
            <h2>Know the best specialist or diagnostic option</h2>
            <p>
              Enter a known diagnosis, specialist, or procedure to see urgency, doctors, and
              hospitals.
            </p>
          </button>

          <button
            type="button"
            className="care-path-card"
            onClick={() => onSelectPath('guided')}
          >
            <span className="care-path-badge">Guided triage</span>
            <h2>Don&apos;t know where to go? Let us help you</h2>
            <p>Describe symptoms and let the existing diagnostic assistant guide the next step.</p>
          </button>
        </div>
      </div>
    </section>
  );
}
