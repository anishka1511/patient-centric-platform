"""
Adapter utilities to convert assessment output into scraping input format.

This module is intentionally side-effect free so it can be introduced
without changing current runtime behavior until explicitly wired in.
"""
from typing import Any, Dict, Optional


def map_urgency_to_severity(urgency_level: Optional[str]) -> str:
    """
    Convert app urgency levels to scraping severity levels.
    Output is always one of: low, medium, high.
    """
    urgency = (urgency_level or "").strip().lower()
    if urgency in {"high", "critical", "emergency"}:
        return "high"
    if urgency == "medium":
        return "medium"
    return "low"


def normalize_specialty(recommended_specialty: Optional[str]) -> str:
    """
    Normalize specialty labels from assessment output to scraping-friendly values.
    """
    specialty = (recommended_specialty or "").strip().lower()
    if not specialty:
        return "general physician"

    replacements = {
        # General medicine
        "general physician / primary care": "general physician",
        "primary care": "general physician",
        "primary care physician": "general physician",
        "general practitioner": "general physician",
        "family physician": "general physician",
        "internal medicine": "general physician",
        "emergency medicine": "general physician",
        # Dentistry
        "dentistry": "dentist",
        "dental": "dentist",
        "dental surgeon": "dentist",
        "oral medicine": "dentist",
        "oral surgery": "dentist",
        # Cardiovascular
        "cardiology": "cardiologist",
        "cardiac specialist": "cardiologist",
        # Skin
        "dermatology": "dermatologist",
        "skin specialist": "dermatologist",
        # Endocrine
        "endocrinology": "endocrinologist",
        # Gastro
        "gastroenterology": "gastroenterologist",
        # Neurology (closest available in current dataset)
        "neurologist": "internal medicine",
        "neurology": "internal medicine",
        # ENT
        "ent": "ent specialist",
        "ear nose throat": "ent specialist",
        "otolaryngologist": "ent specialist",
        # Orthopedics
        "orthopaedic": "orthopedic",
        "orthopedics": "orthopedic",
        # Gynecology/OBGYN
        "gynecologist": "gynac",
        "gynaecologist": "gynac",
        "gynecology": "gynac",
        "obstetrician": "obsstetrician",
        "obstetrics": "obsstetrician",
        "obstetrics and gynaecology": "gynac",
        "ob gyn": "gynac",
        "obgyn": "gynac",
        # Pediatrics
        "paediatrician": "pediatrician",
        "pediatrics": "pediatrician",
        # Kidney and cancer
        "nephrology": "nephrologist",
        "oncology": "oncologist",
        # Eye
        "eye specialist": "ophthalmologist",
        "ophthalmology": "ophthalmologist",
        # Respiratory
        "chest physician": "pulmonologist",
        "pulmonology": "pulmonologist",
        # Urinary and mental health
        "urology": "urologist",
        "psychiatry": "psychiatrist",
        # Mental health
        "mental health specialist": "psychiatrist",
    }
    if specialty in replacements:
        return replacements[specialty]

    # Keep specialty text stable while removing separator noise.
    return specialty.replace("/", " ").replace("  ", " ").strip()


def build_scraping_input(
    assessment_result: Dict[str, Any],
    location: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build payload expected by scraping recommendation logic:
    {
      "severity": "low|medium|high",
      "location": {"latitude": <float>, "longitude": <float>},
      "specialty": "<doctor type>"
    }
    """
    loc = location or {}

    latitude = loc.get("latitude")
    longitude = loc.get("longitude")
    city = (loc.get("city") or "").strip()

    # Support both coordinate and region-name flows:
    # - coordinates: {"latitude": ..., "longitude": ...}
    # - region name: "kothrud"
    normalized_location: Any
    if latitude is not None and longitude is not None:
        normalized_location = {
            "latitude": latitude,
            "longitude": longitude,
        }
    elif city:
        normalized_location = city
    else:
        normalized_location = {
            "latitude": None,
            "longitude": None,
        }

    payload = {
        "severity": map_urgency_to_severity(assessment_result.get("urgency_level")),
        "location": normalized_location,
        "specialty": normalize_specialty(
            assessment_result.get("recommended_specialty")
        ),
    }
    return payload
