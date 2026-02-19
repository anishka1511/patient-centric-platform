from typing import Any


REVIEW_INTEL: dict[str, dict[str, Any]] = {
	"citycare multispeciality": {
		"review_score": 4.3,
		"sentiment_summary": "Positive overall feedback for staff behavior and timely care.",
		"hidden_charges_risk": "low",
	},
	"apex heart & trauma": {
		"review_score": 4.5,
		"sentiment_summary": "Strong clinical outcomes, but occasional billing escalation.",
		"hidden_charges_risk": "medium",
	},
	"greenlife clinic": {
		"review_score": 4.0,
		"sentiment_summary": "Affordable and quick consults; mixed follow-up experience.",
		"hidden_charges_risk": "low",
	},
	"metropulse hospital": {
		"review_score": 4.6,
		"sentiment_summary": "High satisfaction for specialist consultations and diagnostics.",
		"hidden_charges_risk": "low",
	},
	"wellspring medical center": {
		"review_score": 4.2,
		"sentiment_summary": "Good value-for-money and insurance processing support.",
		"hidden_charges_risk": "low",
	},
}


def get_review_intel(hospital_name: str) -> dict[str, Any]:
	key = hospital_name.strip().lower()
	return REVIEW_INTEL.get(
		key,
		{
			"review_score": 3.8,
			"sentiment_summary": "Limited feedback available for this provider.",
			"hidden_charges_risk": "medium",
		},
	)
