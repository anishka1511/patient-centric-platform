from typing import Literal, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.orchestrator.aggregator import run_orchestration
from services.agent_orchestrator import agent_orchestrator
from data_loader import generate_recommendation_response

router = APIRouter(prefix="/api", tags=["analyze"])


class AnalyzeRequest(BaseModel):
	patient_id: str | None = None
	age: int | None = Field(default=None, ge=0, le=120)
	gender: str | None = None
	symptoms: list[str] = Field(..., min_length=1)
	city: str = Field(..., min_length=1)
	insurance_provider: str | None = None


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
	rank_score: float | None = None
	rank_reasons: list[str]
	estimated_cost_for_hospital: int | None = Field(default=None, ge=0)


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
	cost_overview: CostOverview | None = None
	meta: Meta


class FullAnalyzeRequest(BaseModel):
	message: str = Field(..., min_length=1)
	city: str | None = None
	age: int | None = Field(default=None, ge=0, le=120)
	gender: str | None = None
	insurance_provider: str | None = None
	session_id: str | None = None
	top_k: int = Field(default=5, ge=1, le=20)


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


@router.post("/full-analyze")
def full_analyze(payload: FullAnalyzeRequest) -> dict[str, Any]:
	"""
	Single-call pipeline:
	1) LLM assessment from raw user input
	2) Orchestrator hospital analysis
	3) Doctor recommendations and cost summary
	"""
	try:
		resolved_city = payload.city or "Pune"

		assessment = agent_orchestrator.assess_user_input(
			user_message=payload.message,
			session_id=payload.session_id,
		)

		category = assessment.get("category")
		if category in {"IRRELEVANT", "INSUFFICIENT_INFO"}:
			return {
				"status": "needs_clarification",
				"assessment": assessment,
				"orchestration": None,
				"doctor_recommendations": None,
				"pipeline": {
					"input_message": payload.message,
					"city": resolved_city,
					"passed_to_orchestrator": False,
				},
			}

		symptoms = assessment.get("symptoms_identified") or assessment.get("symptoms") or []
		if not symptoms:
			raise HTTPException(
				status_code=422,
				detail={
					"message": "No symptoms extracted from input; cannot run orchestrator.",
					"error_type": "NoSymptomsExtracted",
				},
			)

		orchestration_payload = {
			"age": payload.age,
			"gender": payload.gender,
			"symptoms": symptoms,
			"city": resolved_city,
			"insurance_provider": payload.insurance_provider,
		}
		orchestration_result = run_orchestration(orchestration_payload)

		specialty = (
			orchestration_result.get("triage", {}).get("specialty")
			or assessment.get("recommended_specialty")
			or "General Physician"
		)
		recommendation_result = generate_recommendation_response(
			{
				"specialty": specialty,
				"location": resolved_city,
				"top_k": payload.top_k,
			}
		)

		return {
			"status": "success",
			"assessment": assessment,
			"orchestration": orchestration_result,
			"doctor_recommendations": recommendation_result,
			"pipeline": {
				"input_message": payload.message,
				"symptoms_forwarded": symptoms,
				"specialty_forwarded": specialty,
				"city": resolved_city,
				"passed_to_orchestrator": True,
			},
		}
	except HTTPException:
		raise
	except Exception as exc:
		raise HTTPException(
			status_code=500,
			detail={
				"message": "Failed to complete full analysis pipeline.",
				"error_type": type(exc).__name__,
			},
		) from exc
