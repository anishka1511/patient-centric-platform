"""
API routes for patient-submitted treatment reviews.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.config.logging_config import logger
from backend.models.review import Review
from backend.routers.schemas import ReviewCreateRequest, ReviewListResponse, ReviewResponse
from backend.services.review_service import review_service

router = APIRouter(prefix="/api", tags=["reviews"])


def _serialize_review(review: Review) -> ReviewResponse:
    factor_ratings = review.factor_ratings if isinstance(review.factor_ratings, dict) else {}
    return ReviewResponse(
        id=review.id,
        doctor_name=review.doctor_name,
        doctor_specialty=review.doctor_specialty,
        facility_name=review.facility_name,
        facility_type=review.facility_type,
        facility_location=review.facility_location,
        reviewer_name=review.reviewer_name,
        comment=review.comment,
        overall_rating=review.overall_rating,
        factor_ratings=factor_ratings,
        additional_charges_paid=review.additional_charges_paid,
        additional_charges_amount=review.additional_charges_amount,
        additional_charges_explained=review.additional_charges_explained,
        created_at=review.created_at,
    )


@router.get("/reviews", response_model=ReviewListResponse)
async def list_reviews(
    doctor_name: Optional[str] = Query(default=None),
    facility_name: Optional[str] = Query(default=None),
    facility_location: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Fetch reviews with optional doctor/facility/location filters.
    """
    try:
        reviews = review_service.list_reviews(
            db,
            doctor_name=doctor_name,
            facility_name=facility_name,
            facility_location=facility_location,
            limit=limit,
        )
        return ReviewListResponse(reviews=[_serialize_review(review) for review in reviews])
    except Exception as exc:
        logger.error("Error fetching reviews: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load reviews") from exc


@router.post("/reviews", response_model=ReviewResponse, status_code=201)
async def create_review(
    payload: ReviewCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Save a patient review for a doctor/facility.
    """
    try:
        review = review_service.create_review(db, payload.model_dump())
        return _serialize_review(review)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Error creating review: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save review") from exc
