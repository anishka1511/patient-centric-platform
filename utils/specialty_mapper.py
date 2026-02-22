"""
Specialty Mapping Logic
Maps symptoms to appropriate medical specialties
"""
import re
from typing import Dict, List, Optional, Tuple


class SpecialtyMapper:
    """
    Rule-based specialty mapping to augment LLM recommendations
    """
    
    # Specialty mappings based on symptom keywords
    SPECIALTY_MAP = {
        "Cardiology": [
            "chest pain", "heart", "palpitation", "irregular heartbeat",
            "shortness of breath", "cardiac", "cardiologist"
        ],
        "Dermatology": [
            "skin", "rash", "acne", "mole", "lesion", "itch", "dermatitis",
            "psoriasis", "eczema", "hives", "dermatologist"
        ],
        "Dentist": [
            "dentist", "dentists", "dental", "tooth", "teeth", "gum", "jaw pain",
            "toothache", "tooth pain", "tooth filling", "dental filling", "root canal",
            "wisdom tooth", "cavity", "oral", "mouth pain", "braces"
        ],
        "ENT Specialist": [
            "ear", "nose", "throat", "sinus", "hearing", "tinnitus",
            "sore throat", "nasal", "ear pain", "hoarse", "ent specialist"
        ],
        "Orthopedic": [
            "bone", "joint", "fracture", "sprain", "back pain", "knee",
            "shoulder", "hip", "arthritis", "musculoskeletal", "orthopedic"
        ],
        "Gynecologist": [
            "pregnancy", "menstrual", "pelvic", "vaginal", "ovarian",
            "uterine", "breast", "period", "gynecologist", "gynaecologist"
        ],
        "Gastroenterologist": [
            "stomach", "abdominal", "digestive", "bowel", "diarrhea",
            "constipation", "nausea", "vomiting", "acid reflux", "gastroenterologist"
        ],
        "Neurologist": [
            "headache", "migraine", "seizure", "numbness", "tingling",
            "memory", "dizziness", "vertigo", "neurological", "neurologist"
        ],
        "Ophthalmologist": [
            "eye", "vision", "blurry", "sight", "optical", "retina", "ophthalmologist"
        ],
        "Pulmonologist": [
            "lung", "breathing", "asthma", "cough", "respiratory",
            "pneumonia", "bronchitis", "pulmonologist"
        ],
        "Urologist": [
            "urinary", "bladder", "kidney", "urine", "prostate", "urologist"
        ],
        "Endocrinologist": [
            "diabetes", "thyroid", "hormone", "insulin", "metabolism", "endocrinologist"
        ],
        "Psychiatrist": [
            "depression", "anxiety", "mental health", "panic", "mood",
            "stress", "psychiatric", "psychiatrist"
        ],
        "General Physician": [
            "general physician", "general doctor", "family doctor",
            "primary care", "internal medicine"
        ],
    }

    # Direct text-to-specialty mapping for known diagnosis/procedure/specialist flow.
    DIRECT_SPECIALTY_PATTERNS = {
        "Dentist": [
            "dentist", "dentists", "dental", "dental surgeon", "tooth", "teeth",
            "tooth pain", "toothache", "tooth filling", "filling", "root canal",
            "cavity", "gum", "gingivitis", "oral surgery", "braces", "orthodontic",
        ],
        "Cardiology": [
            "cardiologist", "cardiology", "heart specialist", "cardiac", "heart",
            "cardiac arrest", "angina", "arrhythmia", "palpitations",
        ],
        "Dermatology": [
            "dermatologist", "dermatology", "skin specialist", "eczema", "psoriasis",
            "acne", "skin rash", "dermatitis", "fungal infection",
        ],
        "ENT Specialist": [
            "ent", "ear nose throat", "otolaryngologist", "sinus", "tonsillitis",
            "ear pain", "hearing loss", "sore throat",
        ],
        "Orthopedic": [
            "orthopedic", "orthopaedic", "bone specialist", "joint pain",
            "fracture", "sprain", "ligament", "arthritis",
        ],
        "Gynecologist": [
            "gynecologist", "gynaecologist", "obgyn", "ob gyn", "gynac",
            "pregnancy", "pcos", "period pain", "menstrual",
        ],
        "Gastroenterologist": [
            "gastroenterologist", "gastro", "acid reflux", "ibs", "gastritis",
            "ulcer", "abdominal pain", "digestive",
        ],
        "Neurologist": [
            "neurologist", "neurology", "migraine", "seizure", "epilepsy",
            "nerve pain", "vertigo",
        ],
        "Ophthalmologist": [
            "ophthalmologist", "eye specialist", "vision", "retina", "cataract",
            "glaucoma", "eye pain",
        ],
        "Pulmonologist": [
            "pulmonologist", "chest physician", "asthma", "copd", "respiratory",
            "pneumonia", "bronchitis",
        ],
        "Urologist": [
            "urologist", "kidney stone", "uti", "prostate", "urinary",
        ],
        "Endocrinologist": [
            "endocrinologist", "diabetes", "thyroid", "hormonal",
        ],
        "Psychiatrist": [
            "psychiatrist", "depression", "anxiety", "panic attack", "mental health",
        ],
        "Oncologist": [
            "oncologist", "oncology", "cancer", "chemotherapy",
        ],
        "Nephrologist": [
            "nephrologist", "nephrology", "kidney failure", "renal",
        ],
        "Pediatrician": [
            "pediatrician", "paediatrician", "child specialist", "newborn",
        ],
        "General Physician": [
            "general physician", "general doctor", "family physician", "primary care",
            "internal medicine",
        ],
    }

    # LLM output normalization to canonical specialty names used by mapper.
    SPECIALTY_ALIASES = {
        "cardiologist": "Cardiology",
        "cardiology": "Cardiology",
        "dermatologist": "Dermatology",
        "dermatology": "Dermatology",
        "dentist": "Dentist",
        "dentistry": "Dentist",
        "dental": "Dentist",
        "dental surgeon": "Dentist",
        "ent": "ENT Specialist",
        "otolaryngologist": "ENT Specialist",
        "orthopedic": "Orthopedic",
        "orthopaedic": "Orthopedic",
        "gynecologist": "Gynecologist",
        "gynaecologist": "Gynecologist",
        "gynac": "Gynecologist",
        "obstetrician": "Gynecologist",
        "gastroenterologist": "Gastroenterologist",
        "neurologist": "Neurologist",
        "ophthalmologist": "Ophthalmologist",
        "pulmonologist": "Pulmonologist",
        "urologist": "Urologist",
        "endocrinologist": "Endocrinologist",
        "psychiatrist": "Psychiatrist",
        "nephrologist": "Nephrologist",
        "oncologist": "Oncologist",
        "pediatrician": "Pediatrician",
        "paediatrician": "Pediatrician",
        "general physician": "General Physician",
        "general practitioner": "General Physician",
        "primary care": "General Physician",
        "primary care physician": "General Physician",
        "internal medicine": "General Physician",
        "emergency medicine": "General Physician",
    }

    def _normalize_text(self, text: str) -> str:
        cleaned = re.sub(r"[^a-z0-9\s]+", " ", str(text or "").lower())
        return re.sub(r"\s+", " ", cleaned).strip()

    def normalize_specialty_label(self, specialty: Optional[str]) -> Optional[str]:
        """
        Normalize a free-form specialty label to the mapper's canonical labels.
        """
        if not specialty:
            return None

        normalized = self._normalize_text(specialty)
        if not normalized:
            return None

        if specialty in self.SPECIALTY_MAP:
            return specialty

        return self.SPECIALTY_ALIASES.get(normalized, specialty)

    def extract_specialty_from_text(self, text: str) -> Tuple[Optional[str], float, List[str]]:
        """
        Detect a specialty directly from known specialist/procedure/diagnosis terms.
        """
        normalized = self._normalize_text(text)
        if not normalized:
            return (None, 0.0, [])

        best_specialty = None
        best_score = 0
        best_terms: List[str] = []

        for specialty, terms in self.DIRECT_SPECIALTY_PATTERNS.items():
            matched_terms = [term for term in terms if term in normalized]
            if not matched_terms:
                continue

            # Weight by number of matched terms and term specificity.
            score = sum(2 if " " in term else 1 for term in matched_terms)
            if score > best_score:
                best_score = score
                best_specialty = specialty
                best_terms = matched_terms

        if not best_specialty:
            return (None, 0.0, [])

        confidence = min(0.8 + (0.06 * best_score), 0.99)
        return (best_specialty, confidence, sorted(set(best_terms), key=len, reverse=True))
    
    def map_specialty(self, symptoms: List[str], llm_specialty: str = None) -> Tuple[str, float]:
        """
        Map symptoms to appropriate specialty
        
        Args:
            symptoms: List of symptoms
            llm_specialty: LLM's recommended specialty (if any)
            
        Returns:
            Tuple of (specialty_name, confidence_score)
        """
        normalized_llm_specialty = self.normalize_specialty_label(llm_specialty)
        direct_from_llm, llm_direct_confidence, _ = self.extract_specialty_from_text(
            llm_specialty or ""
        )

        if not symptoms:
            if direct_from_llm:
                return (direct_from_llm, llm_direct_confidence)
            if normalized_llm_specialty:
                return (normalized_llm_specialty, 0.7)
            return ("General Physician", 0.5)

        symptoms_text = self._normalize_text(" ".join(symptoms))

        # Highest-priority deterministic mapping for known terms.
        direct_specialty, direct_confidence, _ = self.extract_specialty_from_text(symptoms_text)
        if direct_specialty:
            return (direct_specialty, direct_confidence)
        
        # Score each specialty
        scores: Dict[str, int] = {}
        for specialty, keywords in self.SPECIALTY_MAP.items():
            score = sum(2 if " " in keyword else 1 for keyword in keywords if keyword.lower() in symptoms_text)
            if score > 0:
                scores[specialty] = score
        
        # If we have a match
        if scores:
            best_specialty = max(scores, key=scores.get)
            max_score = scores[best_specialty]
            confidence = min(0.6 + (0.08 * max_score), 0.95)
            
            # If LLM provided a specialty and it's in our top matches, prefer it
            if normalized_llm_specialty and normalized_llm_specialty in scores:
                return (normalized_llm_specialty, 0.9)
            
            return (best_specialty, confidence)
        
        if direct_from_llm:
            return (direct_from_llm, llm_direct_confidence)

        # If LLM provided something, use it
        if normalized_llm_specialty:
            return (normalized_llm_specialty, 0.7)
        
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
