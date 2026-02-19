from typing import Any


def analyze_symptoms(symptoms: list[str], age: int | None = None) -> dict[str, Any]:
	lowered = " ".join(symptoms).lower()

	emergency_keywords = [
		"chest pain",
		"breathlessness",
		"shortness of breath",
		"stroke",
		"seizure",
		"unconscious",
		"severe bleeding",
	]
	emergency = any(keyword in lowered for keyword in emergency_keywords)

	mapping = {
		"fever": "general physician",
		"cold": "general physician",
		"cough": "pulmonology",
		"skin rash": "dermatology",
		"headache": "neurology",
		"chest pain": "cardiology",
		"pregnancy": "gynecology",
		"fracture": "orthopedics",
		"stomach": "gastroenterology",
	}

	specialty = "general physician"
	for key, value in mapping.items():
		if key in lowered:
			specialty = value
			break

	if emergency:
		urgency = "critical"
		confidence = 0.96
		rationale = "Emergency symptom keyword detected."
	elif "severe" in lowered:
		urgency = "high"
		confidence = 0.83
		rationale = "Severity cue detected in symptom description."
	elif age is not None and age >= 65:
		urgency = "medium"
		confidence = 0.78
		rationale = "Symptoms are non-critical but age increases risk."
	else:
		urgency = "low"
		confidence = 0.75
		rationale = "Common non-emergency symptom pattern."

	return {
		"specialty": specialty,
		"urgency_level": urgency,
		"emergency": emergency,
		"confidence": confidence,
		"rationale": rationale,
	}
