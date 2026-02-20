from typing import Any

from backend.agents.mock_symptom_agent import analyze_symptoms as analyze_symptoms_mock
from config.logging_config import logger
from utils.emergency_rules import emergency_detector
from utils.specialty_mapper import specialty_mapper

try:
	from services.llm_service import llm_service
except Exception as import_error:
	llm_service = None
	logger.warning(
		"LLM service unavailable in symptom_agent; falling back to mock symptom analyzer: %s",
		import_error,
	)


SPECIALTY_CANONICAL_MAP = {
	"emergency medicine": "emergency",
	"emergency department": "emergency",
	"emergency": "emergency",
	"cardiology": "cardiology",
	"cardiologist": "cardiology",
	"general physician": "general physician",
	"primary care": "general physician",
	"general practitioner": "general physician",
	"gp": "general physician",
	"dermatology": "dermatology",
	"dermatologist": "dermatology",
	"gynecology": "gynecology",
	"gynecologist": "gynecology",
	"orthopedics": "orthopedics",
	"orthopedic": "orthopedics",
	"neurology": "neurology",
	"neurologist": "neurology",
	"pulmonology": "pulmonology",
	"pulmonologist": "pulmonology",
	"gastroenterology": "gastroenterology",
	"gastroenterologist": "gastroenterology",
	"ent specialist": "general physician",
	"dentist": "general physician",
}


def _canonical_specialty(raw_specialty: str | None, emergency: bool) -> str:
	if emergency:
		return "emergency"

	if not raw_specialty:
		return "general physician"

	normalized = raw_specialty.strip().lower()
	if normalized in SPECIALTY_CANONICAL_MAP:
		return SPECIALTY_CANONICAL_MAP[normalized]

	for key, value in SPECIALTY_CANONICAL_MAP.items():
		if key in normalized:
			return value

	return "general physician"


def analyze_symptoms(symptoms: list[str], age: int | None = None) -> dict[str, Any]:
	if not symptoms:
		return {
			"specialty": "general physician",
			"urgency_level": "low",
			"emergency": False,
			"confidence": 0.55,
			"rationale": "No symptoms provided; defaulting to general physician triage.",
		}

	try:
		if llm_service is None:
			return analyze_symptoms_mock(symptoms=symptoms, age=age)

		llm_assessment = llm_service.assess_symptoms(symptoms)
		symptoms_text = " ".join(symptoms)

		rule_emergency, _, rule_reason = emergency_detector.detect_emergency(symptoms_text, symptoms)
		rule_urgency = emergency_detector.assess_urgency(symptoms_text, symptoms)

		emergency = bool(llm_assessment.get("emergency_flag", False) or rule_emergency)

		urgency = str(llm_assessment.get("urgency_level", "low")).lower()
		if urgency not in {"low", "medium", "high", "critical"}:
			urgency = "low"

		if emergency:
			urgency = "critical"
		else:
			urgency_rank = {"low": 0, "medium": 1, "high": 2, "critical": 3}
			if urgency_rank.get(rule_urgency, 0) > urgency_rank.get(urgency, 0):
				urgency = rule_urgency

		raw_specialty = llm_assessment.get("recommended_specialty")
		mapped_specialty, mapped_confidence = specialty_mapper.map_specialty(symptoms, raw_specialty)
		specialty = _canonical_specialty(raw_specialty or mapped_specialty, emergency)

		confidence = float(llm_assessment.get("confidence", mapped_confidence if mapped_confidence else 0.72))
		confidence = max(0.0, min(1.0, confidence))

		rationale = str(llm_assessment.get("reasoning", "LLM-based symptom triage completed."))
		if rule_emergency and rule_reason:
			rationale = f"{rationale} Rule-based safety check: {rule_reason}."

		if age is not None and age >= 65 and urgency == "low" and not emergency:
			urgency = "medium"
			rationale = f"{rationale} Age-sensitive adjustment applied."

		return {
			"specialty": specialty,
			"urgency_level": urgency,
			"emergency": emergency,
			"confidence": confidence,
			"rationale": rationale,
		}

	except Exception as error:
		logger.error("LLM symptom agent failed, using mock analyzer: %s", error, exc_info=True)
		return analyze_symptoms_mock(symptoms=symptoms, age=age)