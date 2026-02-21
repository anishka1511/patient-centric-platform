from typing import Any


def estimate_cost(
	specialty: str,
	urgency_level: str,
	insurance_provider: str | None,
) -> dict[str, Any]:
	specialty_base = {
		"general physician": 1200,
		"cardiology": 3500,
		"orthopedics": 2800,
		"neurology": 4200,
		"pulmonology": 2600,
		"dermatology": 1500,
		"gynecology": 2200,
		"gastroenterology": 3000,
	}

	urgency_multiplier = {
		"low": 1.0,
		"medium": 1.2,
		"high": 1.5,
		"critical": 2.2,
	}

	base_cost = specialty_base.get(specialty.lower(), 2000)
	multiplier = urgency_multiplier.get(urgency_level.lower(), 1.0)
	gross = int(base_cost * multiplier)

	insurance_discount = 0.18 if insurance_provider else 0.0
	net = int(gross * (1 - insurance_discount))

	return {
		"currency": "INR",
		"estimated_min": int(net * 0.85),
		"estimated_max": int(net * 1.25),
		"estimated_avg": net,
		"breakdown": {
			"consultation": int(net * 0.25),
			"diagnostics": int(net * 0.35),
			"medication": int(net * 0.20),
			"procedures": int(net * 0.20),
		},
		"insurance_applied": bool(insurance_provider),
	}
