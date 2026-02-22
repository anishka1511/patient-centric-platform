import '../styles/HospitalCard.css';

export default function HospitalCard({ hospital }) {
  const { name, distance_km, rating, cost_level, insurance_supported } = hospital;

  const getCostBadgeClass = () => {
    switch (cost_level) {
      case 'high':
        return 'cost-badge cost-high';
      case 'medium':
        return 'cost-badge cost-medium';
      case 'low':
        return 'cost-badge cost-low';
      default:
        return 'cost-badge';
    }
  };

  const formatCostLevel = (level) => {
    return level.charAt(0).toUpperCase() + level.slice(1);
  };

  return (
    <div className="hospital-card">
      <div className="card-header">
        <h3 className="hospital-name">{name}</h3>
      </div>

      <div className="card-body">
        <div className="hospital-info">
          <div className="info-item">
            <span className="info-label">Distance</span>
            <span className="info-value">{distance_km} km</span>
          </div>

          <div className="info-item">
            <span className="info-label">Rating</span>
            <span className="info-value">
              {'⭐'.repeat(Math.floor(rating))} {rating}
            </span>
          </div>
        </div>

        <div className="card-footer">
          <span className={getCostBadgeClass()}>
            {formatCostLevel(cost_level)}
          </span>
          {insurance_supported && (
            <span className="insurance-badge">✓ Insurance</span>
          )}
        </div>
      </div>
    </div>
  );
}
