from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from config.database import Base


class UrgencyLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CareSetting(str, enum.Enum):
    CLINIC = "clinic"
    SPECIALIST_VISIT = "specialist_visit"
    EMERGENCY_DEPARTMENT = "emergency_department"


class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False, index=True)
    
    # Extracted symptoms
    symptoms_identified = Column(JSON, nullable=False)  # List of symptoms
    
    # Assessment results
    urgency_level = Column(Enum(UrgencyLevel), nullable=False)
    emergency_flag = Column(Boolean, default=False, nullable=False)
    recommended_specialty = Column(String, nullable=False)
    care_setting = Column(Enum(CareSetting), nullable=False)
    
    # Reasoning and advice
    reasoning = Column(Text, nullable=False)
    safety_advice = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="assessments")
    
    def __repr__(self):
        return f"<Assessment(id={self.id}, urgency={self.urgency_level}, emergency={self.emergency_flag})>"
