import '../styles/UrgencyBanner.css';

export default function UrgencyBanner({ urgency, emergency_flag }) {
  const getColorClass = () => {
    if (emergency_flag) return 'banner-emergency';
    switch (urgency) {
      case 'high':
        return 'banner-high';
      case 'medium':
        return 'banner-medium';
      case 'low':
        return 'banner-low';
      default:
        return 'banner-low';
    }
  };

  const getTitle = () => {
    if (emergency_flag) return '🚨 EMERGENCY - Seek Care Immediately';
    switch (urgency) {
      case 'high':
        return '⚠️ High Urgency - Seek Care Soon';
      case 'medium':
        return '📋 Medium Urgency - Schedule an Appointment';
      case 'low':
        return '✅ Low Urgency - Routine Care';
      default:
        return 'Consult a Healthcare Professional';
    }
  };

  return (
    <div className={`urgency-banner ${getColorClass()}`}>
      <h2>{getTitle()}</h2>
    </div>
  );
}
