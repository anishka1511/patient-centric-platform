from datetime import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, JSON, String, Text

from backend.config.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    doctor_name = Column(String, nullable=False, index=True)
    doctor_specialty = Column(String, nullable=True, index=True)
    facility_name = Column(String, nullable=True, index=True)
    facility_type = Column(String, nullable=True)
    facility_location = Column(String, nullable=True, index=True)

    reviewer_name = Column(String, nullable=True)
    comment = Column(Text, nullable=False)
    overall_rating = Column(Float, nullable=False)
    factor_ratings = Column(JSON, nullable=False, default=dict)

    additional_charges_paid = Column(Boolean, nullable=True)
    additional_charges_amount = Column(String, nullable=True)
    additional_charges_explained = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return (
            f"<Review(id={self.id}, doctor_name={self.doctor_name}, "
            f"facility_location={self.facility_location})>"
        )
