from typing import Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.orchestrator.aggregator import run_orchestration

router = APIRouter(prefix="/api", tags=["analyze"])


class AnalyzeRequest(BaseModel):
	patient_id: Optional[str] = None
	age: Optional[int] = Field(default=None, ge=0, le=120)
	gender: Optional[str] = None
	symptoms: list[str] = Field(..., min_length=1)
	city: str = Field(..., min_length=1)
	insurance_provider: Optional[str] = None


class Triage(BaseModel):
	specialty: str
	urgency_level: Literal["low", "medium", "high", "critical"]
	emergency: bool
	confidence: float = Field(..., ge=0, le=1)
	rationale: str


class HospitalRecommendation(BaseModel):
	hospital_name: str
	distance_km: float = Field(..., ge=0)
	rating: float = Field(..., ge=0, le=5)
	estimated_wait_time_min: int = Field(..., ge=0)
	accepts_insurance: bool
	review_summary: str
	hidden_charges_risk: Literal["low", "medium", "high", "unknown"]
	rank_score: Optional[float] = None
	rank_reasons: list[str]
	estimated_cost_for_hospital: Optional[int] = Field(default=None, ge=0)


class CostBreakdown(BaseModel):
	consultation: int = Field(..., ge=0)
	diagnostics: int = Field(..., ge=0)
	medication: int = Field(..., ge=0)
	procedures: int = Field(..., ge=0)


class CostOverview(BaseModel):
	currency: str
	estimated_min: int = Field(..., ge=0)
	estimated_max: int = Field(..., ge=0)
	estimated_avg: int = Field(..., ge=0)
	breakdown: CostBreakdown
	insurance_applied: bool


class Meta(BaseModel):
	used_mock_data: bool
	flow: Literal["standard", "emergency"]
	generated_at: str


class AnalyzeResponse(BaseModel):
	triage: Triage
	recommended_action: str
	hospitals: list[HospitalRecommendation]
	cost_overview: Optional[CostOverview] = None
	meta: Meta


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
	try:
		result = run_orchestration(payload.model_dump())
		return AnalyzeResponse.model_validate(result)
	except Exception as exc:
		raise HTTPException(
			status_code=500,
			detail={
				"message": "Failed to complete analysis.",
				"error_type": type(exc).__name__,
			},
		) from exc
