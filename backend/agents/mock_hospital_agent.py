from typing import Any


def _seed_hospitals() -> list[dict[str, Any]]:
	return [
		{
			"hospital_name": "CityCare Multispeciality",
			"city": "pune",
			"specialties": ["cardiology", "general physician", "neurology"],
			"distance_km": 2.8,
			"rating": 4.4,
			"estimated_wait_time_min": 22,
			"tier": "standard",
			"accepted_insurance": ["star", "hdfc ergo", "icici lombard"],
		},
		{
			"hospital_name": "Apex Heart & Trauma",
			"city": "pune",
			"specialties": ["cardiology", "orthopedics", "emergency"],
			"distance_km": 5.1,
			"rating": 4.7,
			"estimated_wait_time_min": 35,
			"tier": "premium",
			"accepted_insurance": ["star", "niva bupa"],
		},
		{
			"hospital_name": "GreenLife Clinic",
			"city": "pune",
			"specialties": ["general physician", "dermatology", "gynecology"],
			"distance_km": 1.9,
			"rating": 4.1,
			"estimated_wait_time_min": 18,
			"tier": "budget",
			"accepted_insurance": ["hdfc ergo", "care"],
		},
		{
			"hospital_name": "MetroPulse Hospital",
			"city": "mumbai",
			"specialties": ["cardiology", "pulmonology", "neurology"],
			"distance_km": 3.5,
			"rating": 4.6,
			"estimated_wait_time_min": 28,
			"tier": "premium",
			"accepted_insurance": ["star", "aditya birla", "icici lombard"],
		},
		{
			"hospital_name": "WellSpring Medical Center",
			"city": "mumbai",
			"specialties": ["general physician", "gastroenterology", "orthopedics"],
			"distance_km": 4.2,
			"rating": 4.3,
			"estimated_wait_time_min": 20,
			"tier": "standard",
			"accepted_insurance": ["hdfc ergo", "care", "niva bupa"],
		},
	]


def find_hospitals(
	city: str,
	specialty: str,
	insurance_provider: str | None,
	emergency: bool = False,
) -> list[dict[str, Any]]:
	city_normalized = city.strip().lower()
	specialty_normalized = specialty.strip().lower()

	hospitals = _seed_hospitals()
	filtered = [item for item in hospitals if item["city"] == city_normalized]

	if specialty_normalized:
		filtered = [
			item
			for item in filtered
			if specialty_normalized in item["specialties"]
			or (emergency and "emergency" in item["specialties"])
		]

	if insurance_provider:
		insurance_key = insurance_provider.strip().lower()
		for item in filtered:
			item["accepts_insurance"] = insurance_key in item["accepted_insurance"]
	else:
		for item in filtered:
			item["accepts_insurance"] = False

	return sorted(filtered, key=lambda item: item["distance_km"])[:5]
