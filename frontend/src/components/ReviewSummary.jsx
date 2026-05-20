import { useEffect, useState } from 'react';
import '../styles/ReviewSummary.css';

export default function ReviewSummary({ doctorName, facilityName }) {
  const [summary, setSummary] = useState({ count: 0, avg: null, topComment: null });
  const key = (doctorName || facilityName || '').trim();

  useEffect(() => {
    if (!key) return;

    const qs = doctorName
      ? `doctor_name=${encodeURIComponent(doctorName)}`
      : `facility_name=${encodeURIComponent(facilityName)}`;

    fetch(`/api/reviews?${qs}`)
      .then((res) => res.json())
      .then((data) => {
        const reviews = Array.isArray(data.reviews) ? data.reviews : [];
        if (reviews.length === 0) {
          setSummary({ count: 0, avg: null, topComment: null });
          return;
        }

        const count = reviews.length;
        const avg = (
          reviews.reduce((s, r) => s + Number(r.overall_rating || 0), 0) / count
        ).toFixed(1);
        const topComment = reviews[0]?.comment ?? null;
        setSummary({ count, avg, topComment });
      })
      .catch(() => {
        setSummary({ count: 0, avg: null, topComment: null });
      });
  }, [doctorName, facilityName, key]);

  if (summary.count === 0) {
    return <div className="review-summary">No reviews yet</div>;
  }

  return (
    <div className="review-summary">
      <div className="review-stats">{summary.count} review{summary.count>1? 's':''} • {summary.avg}/5</div>
      {summary.topComment && <div className="review-top">“{summary.topComment}”</div>}
    </div>
  );
}
