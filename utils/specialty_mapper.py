"""
Specialty Mapping Logic
Maps symptoms to appropriate medical specialties
"""
from typing import List, Tuple


class SpecialtyMapper:
    """
    Rule-based specialty mapping to augment LLM recommendations
    """
    
    # Specialty mappings based on symptom keywords
    SPECIALTY_MAP = {
        "Cardiology": [
            "chest pain", "heart", "palpitation", "irregular heartbeat",
            "shortness of breath", "cardiac"
        ],
        "Dermatology": [
            "skin", "rash", "acne", "mole", "lesion", "itch", "dermatitis",
            "psoriasis", "eczema", "hives"
        ],
        "Dentist": [
            "tooth", "teeth", "dental", "gum", "jaw pain", "toothache",
            "cavity", "mouth pain"
        ],
        "ENT Specialist": [
            "ear", "nose", "throat", "sinus", "hearing", "tinnitus",
            "sore throat", "nasal", "ear pain", "hoarse"
        ],
        "Orthopedic": [
            "bone", "joint", "fracture", "sprain", "back pain", "knee",
            "shoulder", "hip", "arthritis", "musculoskeletal"
        ],
        "Gynecologist": [
            "pregnancy", "menstrual", "pelvic", "vaginal", "ovarian",
            "uterine", "breast", "period"
        ],
        "Gastroenterologist": [
            "stomach", "abdominal", "digestive", "bowel", "diarrhea",
            "constipation", "nausea", "vomiting", "acid reflux"
        ],
        "Neurologist": [
            "headache", "migraine", "seizure", "numbness", "tingling",
            "memory", "dizziness", "vertigo", "neurological"
        ],
        "Ophthalmologist": [
            "eye", "vision", "blurry", "sight", "optical", "retina"
        ],
        "Pulmonologist": [
            "lung", "breathing", "asthma", "cough", "respiratory",
            "pneumonia", "bronchitis"
        ],
        "Urologist": [
            "urinary", "bladder", "kidney", "urine", "prostate"
        ],
        "Endocrinologist": [
            "diabetes", "thyroid", "hormone", "insulin", "metabolism"
        ],
        "Psychiatrist": [
            "depression", "anxiety", "mental health", "panic", "mood",
            "stress", "psychiatric"
        ]
    }
    
    def map_specialty(self, symptoms: List[str], llm_specialty: str = None) -> Tuple[str, float]:
        """
        Map symptoms to appropriate specialty
        
        Args:
            symptoms: List of symptoms
            llm_specialty: LLM's recommended specialty (if any)
            
        Returns:
            Tuple of (specialty_name, confidence_score)
        """
        if not symptoms:
            return ("General Physician", 0.5)
        
        symptoms_text = " ".join(symptoms).lower()
        
        # Score each specialty
        scores = {}
        for specialty, keywords in self.SPECIALTY_MAP.items():
            score = sum(1 for keyword in keywords if keyword.lower() in symptoms_text)
            if score > 0:
                scores[specialty] = score
        
        # If we have a match
        if scores:
            best_specialty = max(scores, key=scores.get)
            max_score = scores[best_specialty]
            confidence = min(max_score / 3.0, 1.0)  # Normalize to 0-1
            
            # If LLM provided a specialty and it's in our top matches, prefer it
            if llm_specialty and llm_specialty in scores:
                return (llm_specialty, 0.9)
            
            return (best_specialty, confidence)
        
        # If LLM provided something, use it
        if llm_specialty:
            return (llm_specialty, 0.7)
        
        # Default to General Physician
        return ("General Physician", 0.6)
    
    def get_care_setting(self, urgency_level: str, emergency_flag: bool) -> str:
        """
        Determine appropriate care setting based on urgency
        
        Args:
            urgency_level: 'low', 'medium', or 'high'
            emergency_flag: Whether it's an emergency
            
        Returns:
            Care setting: 'clinic', 'specialist_visit', or 'emergency_department'
        """
        if emergency_flag or urgency_level == 'high':
            return 'emergency_department'
        elif urgency_level == 'medium':
            return 'clinic'
        else:
            return 'clinic'


# Create singleton instance
specialty_mapper = SpecialtyMapper()
