import '../styles/CostPanel.css';

export default function CostPanel({ cost_estimate }) {
  const renderCost = () => {
    if (typeof cost_estimate === 'string') {
      return cost_estimate;
    }

    if (cost_estimate && typeof cost_estimate === 'object') {
      const min = cost_estimate.min_fee ?? cost_estimate.estimated_min;
      const max = cost_estimate.max_fee ?? cost_estimate.estimated_max;
      const avg = cost_estimate.average_fee ?? cost_estimate.estimated_avg;

      if (min != null && max != null) {
        return `Rs.${Math.round(min)} - Rs.${Math.round(max)}`;
      }
      if (avg != null) {
        return `Approx. Rs.${Math.round(avg)}`;
      }
    }

    return 'Contact provider for pricing';
  };

  return (
    <div className="cost-panel">
      <h3>Estimated Cost Range</h3>
      <p className="cost-amount">{renderCost()}</p>
      <p className="cost-disclaimer">
        *Estimates are approximate and may vary by hospital and treatment specifics.
      </p>
    </div>
  );
}
