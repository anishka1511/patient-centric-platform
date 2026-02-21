from datetime import datetime, timezone
from typing import Any

from backend.agents.mock_cost_agent import estimate_cost
from backend.agents.mock_hospital_agent import find_hospitals
from backend.agents.mock_review_agent import get_review_intel
from backend.agents.symptom_agent import analyze_symptoms


def _clamp(value: float, minimum: float, maximum: float) -> float:
	return max(minimum, min(value, maximum))


def _tier_multiplier(tier: str) -> float:
	table = {"budget": 0.85, "standard": 1.0, "premium": 1.25}
	return table.get(tier, 1.0)


def _rank_hospitals(
	hospitals: list[dict[str, Any]],
	base_cost_avg: int,
) -> list[dict[str, Any]]:
	if not hospitals:
		return hospitals

	max_distance = max(item["distance_km"] for item in hospitals)
	min_distance = min(item["distance_km"] for item in hospitals)
	distance_span = max(max_distance - min_distance, 0.1)

	ranked: list[dict[str, Any]] = []
	for hospital in hospitals:
		review_info = hospital["review"]
		rating_score = _clamp(hospital["rating"] / 5.0, 0.0, 1.0)
		review_score = _clamp(review_info["review_score"] / 5.0, 0.0, 1.0)
		distance_score = _clamp(
			(max_distance - hospital["distance_km"]) / distance_span,
			0.0,
			1.0,
		)

		estimated_cost = int(base_cost_avg * _tier_multiplier(hospital["tier"]))
		affordability_score = _clamp(1 - (estimated_cost / (base_cost_avg * 1.4)), 0.0, 1.0)

		weighted_score = (
			0.35 * rating_score
			+ 0.25 * distance_score
			+ 0.25 * affordability_score
			+ 0.15 * review_score
		)

		hospital["rank_score"] = round(weighted_score * 100, 2)
		hospital["estimated_cost_for_hospital"] = estimated_cost
		hospital["rank_reasons"] = [
			f"Rating score: {rating_score:.2f}",
			f"Distance score: {distance_score:.2f}",
			f"Affordability score: {affordability_score:.2f}",
			f"Review score: {review_score:.2f}",
		]
		ranked.append(hospital)

	ranked.sort(key=lambda item: item["rank_score"], reverse=True)
	return ranked


def run_orchestration(payload: dict[str, Any]) -> dict[str, Any]:
	symptoms = payload.get("symptoms", [])
	age = payload.get("age")
	city = payload.get("city", "")
	insurance_provider = payload.get("insurance_provider")

	triage = analyze_symptoms(symptoms=symptoms, age=age)

	if triage["emergency"]:
		emergency_hospitals = find_hospitals(
			city=city,
			specialty="emergency",
			insurance_provider=insurance_provider,
			emergency=True,
		)
		hospital_response = [
			{
				"hospital_name": item["hospital_name"],
				"distance_km": item["distance_km"],
				"rating": item["rating"],
				"estimated_wait_time_min": item["estimated_wait_time_min"],
				"accepts_insurance": item["accepts_insurance"],
				"review_summary": "Emergency triage mode: proceed to nearest capable center.",
				"hidden_charges_risk": "unknown",
				"rank_score": None,
				"rank_reasons": [],
				"estimated_cost_for_hospital": None,
			}
			for item in emergency_hospitals
		]

		return {
			"triage": triage,
			"recommended_action": "Immediate emergency care recommended. Call emergency services or visit nearest ER.",
			"hospitals": hospital_response,
			"cost_overview": None,
			"meta": {
				"used_mock_data": True,
				"flow": "emergency",
				"generated_at": datetime.now(timezone.utc).isoformat(),
			},
		}

	hospitals = find_hospitals(
		city=city,
		specialty=triage["specialty"],
		insurance_provider=insurance_provider,
	)

	cost_data = estimate_cost(
		specialty=triage["specialty"],
		urgency_level=triage["urgency_level"],
		insurance_provider=insurance_provider,
	)

	enriched_hospitals: list[dict[str, Any]] = []
	for hospital in hospitals:
		review_data = get_review_intel(hospital_name=hospital["hospital_name"])
		enriched_hospitals.append({**hospital, "review": review_data})

	ranked = _rank_hospitals(enriched_hospitals, base_cost_avg=cost_data["estimated_avg"])

	response_hospitals = [
		{
			"hospital_name": item["hospital_name"],
			"distance_km": item["distance_km"],
			"rating": item["rating"],
			"estimated_wait_time_min": item["estimated_wait_time_min"],
			"accepts_insurance": item["accepts_insurance"],
			"review_summary": item["review"]["sentiment_summary"],
			"hidden_charges_risk": item["review"]["hidden_charges_risk"],
			"rank_score": item["rank_score"],
			"rank_reasons": item["rank_reasons"],
			"estimated_cost_for_hospital": item["estimated_cost_for_hospital"],
		}
		for item in ranked
	]

	return {
		"triage": triage,
		"recommended_action": "Book a specialist consultation within 24-48 hours.",
		"hospitals": response_hospitals,
		"cost_overview": cost_data,
		"meta": {
			"used_mock_data": True,
			"flow": "standard",
			"generated_at": datetime.now(timezone.utc).isoformat(),
		},
	}
