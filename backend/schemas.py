"""
Data Contracts for Multi-Agent Healthcare System

Defines strict input/output schemas for all agents.
These ensure agents can communicate with orchestrator.
"""

from typing import TypedDict, Literal, Optional
from enum import Enum

# ============================================================================
# ENUMS - Controlled Values
# ============================================================================

class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MedicalSpecialty(str, Enum):
    CARDIOLOGY = "Cardiology"
    DERMATOLOGY = "Dermatology"
    ORTHOPEDICS = "Orthopedics"
    NEUROLOGY = "Neurology"
    GASTROENTEROLOGY = "Gastroenterology"
    RESPIRATORY = "Respiratory"
    GENERAL = "General"
    EMERGENCY = "Emergency"
    PEDIATRICS = "Pediatrics"
    PSYCHIATRY = "Psychiatry"
    ONCOLOGY = "Oncology"
    ENT = "ENT"

# ============================================================================
# SYMPTOM AGENT INPUT/OUTPUT
# ============================================================================

class SymptomAgentInput(TypedDict, total=False):
    """
    Input to Symptom Analysis Agent
    
    Required: symptoms
    Optional: image_base64, location
    """
    symptoms: str  # Patient's symptom description
    image_base64: Optional[str]  # Medical image in base64
    location: Optional[str]  # Patient location (city/area)

class SymptomAgentOutput(TypedDict):
    """
    Output from Symptom Analysis Agent
    
    MUST be returned as structured JSON
    Orchestrator will parse and route based on this
    """
    specialty: MedicalSpecialty
    urgency: UrgencyLevel
    emergency_flag: bool
    confidence: float  # 0.0 to 1.0
    reasoning: str  # Why this classification
    key_findings: list[str]  # Extracted symptom keywords
    recommended_next_steps: list[str]  # Guidance (not diagnosis)

# ============================================================================
# HOSPITAL RECOMMENDER AGENT INPUT/OUTPUT (Template for provided agent)
# ============================================================================

class HospitalRecommenderInput(TypedDict, total=False):
    """Expected input format for Hospital Recommender Agent"""
    specialty: MedicalSpecialty
    location: str
    urgency: UrgencyLevel

class DoctorInfo(TypedDict, total=False):
    name: str
    experience_years: int
    floor: str
    availability: str

class HospitalInfo(TypedDict, total=False):
    name: str
    distance_km: float
    rating: float
    cost_level: Literal["low", "medium", "high"]
    insurance_supported: bool
    doctors: list[DoctorInfo]

class HospitalRecommenderOutput(TypedDict):
    """Expected output format from Hospital Recommender Agent"""
    hospitals: list[HospitalInfo]
    guidance: str
    confidence: float

# ============================================================================
# COST ESTIMATOR AGENT INPUT/OUTPUT (Template for provided agent)
# ============================================================================

class CostEstimatorInput(TypedDict, total=False):
    """Expected input format for Cost Estimator Agent"""
    specialty: MedicalSpecialty
    urgency: UrgencyLevel
    location: Optional[str]

class CostEstimatorOutput(TypedDict):
    """Expected output format from Cost Estimator Agent"""
    estimate: str  # e.g., "₹800–₹2000"
    confidence: float
    breakdown: dict  # Optional: {consultation: 500, tests: 1000, ...}

# ============================================================================
# ORCHESTRATOR OUTPUT (What user gets)
# ============================================================================

class OrchestratorOutput(TypedDict):
    """
    Final output from orchestrator combining all agent results
    This is what frontend receives
    """
    recommendation: str
    urgency: UrgencyLevel
    emergency_flag: bool
    specialty: MedicalSpecialty
    hospitals: list[HospitalInfo]
    cost_estimate: str
    guidance: str
    confidence_score: float

# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_symptom_output(output: dict) -> bool:
    """Validate symptom agent output has all required fields"""
    required_fields = {
        "specialty", "urgency", "emergency_flag", 
        "confidence", "reasoning", "key_findings", "recommended_next_steps"
    }
    return all(field in output for field in required_fields)

def validate_urgency(urgency: str) -> bool:
    """Check if urgency is valid"""
    valid_urgencies = {e.value for e in UrgencyLevel}
    return urgency in valid_urgencies

def validate_specialty(specialty: str) -> bool:
    """Check if specialty is valid"""
    valid_specialties = {e.value for e in MedicalSpecialty}
    return specialty in valid_specialties
