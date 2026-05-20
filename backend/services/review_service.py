from typing import Any, Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.config.logging_config import logger
from backend.models.review import Review


def _normalize_filter(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _normalize_factor_ratings(raw: Optional[Dict[str, Any]]) -> Dict[str, float]:
    if not isinstance(raw, dict):
        return {}

    normalized: Dict[str, float] = {}
    for key, value in raw.items():
        if value is None:
            continue
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        if numeric < 0:
            numeric = 0.0
        if numeric > 5:
            numeric = 5.0
        normalized[str(key)] = round(numeric, 1)
    return normalized


class ReviewService:
    """Service for creating and querying patient treatment reviews."""

    def list_reviews(
        self,
        db: Session,
        doctor_name: Optional[str] = None,
        facility_name: Optional[str] = None,
        facility_location: Optional[str] = None,
        limit: int = 50,
    ) -> list[Review]:
        doctor_filter = _normalize_filter(doctor_name)
        facility_filter = _normalize_filter(facility_name)
        location_filter = _normalize_filter(facility_location)

        query = db.query(Review)

        if doctor_filter:
            query = query.filter(
                func.lower(Review.doctor_name).contains(doctor_filter.lower())
            )
        if facility_filter:
            query = query.filter(
                func.lower(Review.facility_name).contains(facility_filter.lower())
            )
        if location_filter:
            query = query.filter(
                func.lower(Review.facility_location).contains(location_filter.lower())
            )

        safe_limit = min(max(limit, 1), 100)
        reviews = query.order_by(Review.created_at.desc()).limit(safe_limit).all()
        logger.info(
            "Fetched %s reviews (doctor=%s, facility=%s, location=%s, limit=%s)",
            len(reviews),
            doctor_filter,
            facility_filter,
            location_filter,
            safe_limit,
        )
        return reviews

    def create_review(self, db: Session, review_data: Dict[str, Any]) -> Review:
        doctor_name = str(review_data.get("doctor_name") or "").strip()
        comment = str(review_data.get("comment") or "").strip()
        if not doctor_name:
            raise ValueError("doctor_name is required")
        if not comment:
            raise ValueError("comment is required")

        try:
            overall_rating = float(review_data.get("overall_rating"))
        except (TypeError, ValueError):
            raise ValueError("overall_rating must be a number between 0 and 5")
        if overall_rating < 0 or overall_rating > 5:
            raise ValueError("overall_rating must be a number between 0 and 5")

        review = Review(
            doctor_name=doctor_name,
            doctor_specialty=_normalize_filter(review_data.get("doctor_specialty")),
            facility_name=_normalize_filter(review_data.get("facility_name")),
            facility_type=_normalize_filter(review_data.get("facility_type")),
            facility_location=_normalize_filter(review_data.get("facility_location")),
            reviewer_name=_normalize_filter(review_data.get("reviewer_name")),
            comment=comment,
            overall_rating=round(overall_rating, 1),
            factor_ratings=_normalize_factor_ratings(review_data.get("factor_ratings")),
            additional_charges_paid=review_data.get("additional_charges_paid"),
            additional_charges_amount=_normalize_filter(
                review_data.get("additional_charges_amount")
            ),
            additional_charges_explained=_normalize_filter(
                review_data.get("additional_charges_explained")
            ),
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        logger.info(
            "Saved review %s for doctor=%s facility=%s",
            review.id,
            review.doctor_name,
            review.facility_name,
        )
        return review


review_service = ReviewService()
