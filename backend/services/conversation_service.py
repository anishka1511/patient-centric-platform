"""
Conversation Service - Database persistence for conversations and assessments
"""
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from backend.models.conversation import Conversation
from backend.models.message import Message, MessageRole
from backend.models.assessment import Assessment, UrgencyLevel, CareSetting
from backend.config.logging_config import logger


class ConversationService:
    """Service for managing conversations and assessments in database"""
    
    def create_conversation(self, db: Session, session_id: str, user_id: Optional[str] = None) -> Conversation:
        """
        Create a new conversation
        
        Args:
            db: Database session
            session_id: Unique session identifier
            user_id: Optional user identifier
            
        Returns:
            Created Conversation object
        """
        conversation = Conversation(
            session_id=session_id,
            user_id=user_id
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        logger.info(f"Created conversation: {conversation.id}")
        return conversation
    
    def get_conversation(self, db: Session, session_id: str) -> Optional[Conversation]:
        """
        Get conversation by session ID
        
        Args:
            db: Database session
            session_id: Session identifier
            
        Returns:
            Conversation object or None
        """
        return db.query(Conversation).filter(Conversation.session_id == session_id).first()
    
    def get_or_create_conversation(self, db: Session, session_id: str, user_id: Optional[str] = None) -> Conversation:
        """
        Get existing conversation or create new one
        
        Args:
            db: Database session
            session_id: Session identifier
            user_id: Optional user identifier
            
        Returns:
            Conversation object
        """
        conversation = self.get_conversation(db, session_id)
        if not conversation:
            conversation = self.create_conversation(db, session_id, user_id)
        return conversation
    
    def add_message(self, db: Session, conversation_id: str, role: MessageRole, content: str, extra_data: Optional[Dict] = None) -> Message:
        """
        Add a message to conversation
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            role: Message role (user/assistant/system)
            content: Message content
            extra_data: Optional extra data (e.g., location, timestamps, context)
            
        Returns:
            Created Message object
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            extra_data=extra_data
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        logger.info(f"Added {role.value} message to conversation {conversation_id}")
        if extra_data:
            logger.debug(f"Message extra_data: {extra_data}")
        return message
    
    def save_assessment(
        self, 
        db: Session, 
        conversation_id: str, 
        assessment_data: Dict
    ) -> Assessment:
        """
        Save symptom assessment to database
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            assessment_data: Assessment result dictionary
            
        Returns:
            Created Assessment object
        """
        assessment = Assessment(
            conversation_id=conversation_id,
            symptoms_identified=assessment_data.get("symptoms_identified", []),
            urgency_level=UrgencyLevel(assessment_data.get("urgency_level", "low")),
            emergency_flag=assessment_data.get("emergency_flag", False),
            recommended_specialty=assessment_data.get("recommended_specialty", "General Physician"),
            care_setting=CareSetting(assessment_data.get("care_setting", "clinic")),
            reasoning=assessment_data.get("reasoning", ""),
            safety_advice=assessment_data.get("safety_advice")
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        logger.info(f"Saved assessment {assessment.id} for conversation {conversation_id}")
        return assessment
    
    def get_recent_messages(self, db: Session, session_id: str, limit: int = 5) -> List[Dict]:
        """
        Get recent messages from conversation for context
        
        Args:
            db: Database session
            session_id: Session identifier
            limit: Maximum number of recent messages to retrieve
            
        Returns:
            List of recent messages (oldest first)
        """
        conversation = self.get_conversation(db, session_id)
        if not conversation:
            return []
        
        # Get last N messages, ordered chronologically
        recent_messages = conversation.messages[-limit:] if len(conversation.messages) > limit else conversation.messages
        
        return [
            {
                "role": msg.role.value,
                "content": msg.content
            }
            for msg in recent_messages
        ]
    
    def get_conversation_history(self, db: Session, session_id: str) -> Optional[Dict]:
        """
        Get full conversation history with messages and assessments
        
        Args:
            db: Database session
            session_id: Session identifier
            
        Returns:
            Dictionary with conversation data or None
        """
        conversation = self.get_conversation(db, session_id)
        if not conversation:
            return None
        
        messages = [
            {
                "role": msg.role.value,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in conversation.messages
        ]
        
        assessments = [
            {
                "symptoms": assess.symptoms_identified,
                "urgency": assess.urgency_level.value,
                "emergency": assess.emergency_flag,
                "specialty": assess.recommended_specialty,
                "care_setting": assess.care_setting.value,
                "reasoning": assess.reasoning,
                "safety_advice": assess.safety_advice,
                "created_at": assess.created_at.isoformat()
            }
            for assess in conversation.assessments
        ]
        
        return {
            "session_id": conversation.session_id,
            "user_id": conversation.user_id,
            "messages": messages,
            "assessments": assessments,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat()
        }


# Create singleton instance
conversation_service = ConversationService()
