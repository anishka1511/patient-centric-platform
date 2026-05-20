"""
Emergency Detection Rules
Rule-based safety net for detecting emergency conditions
"""
from typing import List, Tuple
import re


class EmergencyDetector:
    """
    Rule-based emergency detection as a safety backup to LLM assessment
    """
    
    # Critical emergency patterns
    EMERGENCY_PATTERNS = [
        # Cardiac/Respiratory
        (r'chest pain.*breath', 'Chest pain with breathing difficulty'),
        (r'severe.*chest pain', 'Severe chest pain'),
        (r"can'?t breathe|cannot breathe|difficulty breathing", 'Severe breathing difficulty'),
        (r'shortness of breath.*chest', 'Breathing difficulty with chest symptoms'),
        
        # Neurological
        (r'stroke|facial droop|face droop', 'Possible stroke symptoms'),
        (r'sudden.*severe headache', 'Sudden severe headache'),
        (r'unconscious|passed out|losing consciousness', 'Loss of consciousness'),
        (r'seizure|convuls', 'Seizure activity'),
        (r'confusion.*sudden|sudden.*confusion', 'Sudden confusion'),
        
        # Trauma/Bleeding
        (r'severe bleeding|heavy bleeding|won\'?t stop bleeding', 'Severe bleeding'),
        (r'serious.*injur|major.*trauma', 'Serious injury or trauma'),
        
        # Critical symptoms
        (r'unable to speak|can\'?t speak', 'Speech difficulty'),
        (r'weakness.*one side|numbness.*one side', 'One-sided weakness/numbness'),
        (r'severe.*pain.*abdomen|severe stomach pain', 'Severe abdominal pain'),
    ]
    
    # High urgency patterns (not immediate emergency but needs prompt care)
    HIGH_URGENCY_PATTERNS = [
        (r'high fever.*infant|baby.*fever', 'High fever in infant'),
        (r'persistent vomiting|severe vomiting', 'Persistent vomiting'),
        (r'severe.*pain', 'Severe pain'),
        (r'worsening rapidly|getting worse fast', 'Rapidly worsening condition'),
    ]
    
    def detect_emergency(self, text: str, symptoms: List[str] = None) -> Tuple[bool, str, str]:
        """
        Detect if text/symptoms indicate an emergency
        
        Args:
            text: User's message text
            symptoms: List of extracted symptoms
            
        Returns:
            Tuple of (is_emergency, matched_pattern, reason)
        """
        text_lower = text.lower()
        
        # Combine text and symptoms for checking
        if symptoms:
            combined_text = text_lower + " " + " ".join(symptoms).lower()
        else:
            combined_text = text_lower
        
        # Check emergency patterns
        for pattern, reason in self.EMERGENCY_PATTERNS:
            if re.search(pattern, combined_text, re.IGNORECASE):
                return (True, pattern, reason)
        
        return (False, None, None)
    
    def assess_urgency(self, text: str, symptoms: List[str] = None) -> str:
        """
        Assess urgency level based on rules
        
        Args:
            text: User's message text
            symptoms: List of extracted symptoms
            
        Returns:
            'high', 'medium', or 'low'
        """
        is_emergency, _, _ = self.detect_emergency(text, symptoms)
        if is_emergency:
            return 'high'
        
        text_lower = text.lower()
        if symptoms:
            combined_text = text_lower + " " + " ".join(symptoms).lower()
        else:
            combined_text = text_lower
        
        # Check high urgency patterns
        for pattern, _ in self.HIGH_URGENCY_PATTERNS:
            if re.search(pattern, combined_text, re.IGNORECASE):
                return 'high'
        
        # Check for medium urgency keywords
        medium_keywords = ['fever', 'persistent', 'severe', 'pain', 'lasting', 'days']
        if any(keyword in combined_text for keyword in medium_keywords):
            return 'medium'
        
        return 'low'


# Create singleton instance
emergency_detector = EmergencyDetector()
