import '../styles/CostPanel.css';

export default function CostPanel({ cost_estimate }) {
  return (
    <div className="cost-panel">
      <h3>Estimated Cost Range</h3>
      <p className="cost-amount">{cost_estimate}</p>
      <p className="cost-disclaimer">
        *Estimates are approximate and may vary by hospital and treatment specifics.
      </p>
    </div>
  );
}
