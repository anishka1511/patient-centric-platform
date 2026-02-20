"""
ORCHESTRATOR INTEGRATION EXAMPLE

This shows how to integrate the Symptom Agent with your provided agents.
Modify this based on your actual orchestrator implementation.

THIS IS A TEMPLATE - Adapt based on your actual agent interfaces.
"""

import asyncio
import json
from typing import Optional
from backend.agents.symptom_agent import symptom_analysis_agent
from backend.schemas import OrchestratorOutput, MedicalSpecialty, UrgencyLevel

# ============================================================================
# PLACEHOLDER AGENT CALLS
# Replace these with your actual agent functions/APIs
# ============================================================================

def call_hospital_recommender_agent(specialty: str, location: str, urgency: str):
    """
    Call your Hospital Recommender Agent
    
    REPLACE THIS with your actual implementation:
    - Call your agent function/API
    - Pass specialty, location, urgency
    - Expect HospitalRecommenderOutput
    """
    # TODO: Replace with actual agent call
    # Example: return requests.post(HOSPITAL_AGENT_API, json={...})
    return {
        "hospitals": [],
        "guidance": "Hospitals recommendations would come here",
        "confidence": 0.0
    }

def call_cost_estimator_agent(specialty: str, urgency: str, location: str = None):
    """
    Call your Cost Estimator Agent
    
    REPLACE THIS with your actual implementation
    """
    # TODO: Replace with actual agent call
    return {
        "estimate": "Cost estimate would come here",
        "confidence": 0.0,
        "breakdown": {}
    }

# ============================================================================
# ORCHESTRATOR (TEMPLATE)
# ============================================================================

async def healthcare_orchestrator(
    symptoms: str,
    location: str = "Default Location",
    image_base64: Optional[str] = None
) -> OrchestratorOutput:
    """
    CENTRAL ORCHESTRATOR
    
    Flow:
    1. Call symptom agent
    2. Check if emergency
    3. If not emergency: call hospital & cost agents
    4. Aggregate results
    5. Return comprehensive output
    
    This is a TEMPLATE. Modify based on your actual agents.
    """
    
    print("\n" + "="*60)
    print("ORCHESTRATOR INVOKED")
    print("="*60)
    
    # STEP 1: Call Symptom Analysis Agent
    print("\n[STEP 1] Calling Symptom Analysis Agent...")
    symptom_result = symptom_analysis_agent(
        symptoms=symptoms,
        image_base64=image_base64
    )
    print(f"✓ Symptom analysis complete")
    print(f"  - Specialty: {symptom_result['specialty']}")
    print(f"  - Urgency: {symptom_result['urgency']}")
    print(f"  - Emergency: {symptom_result['emergency_flag']}")
    print(f"  - Confidence: {symptom_result['confidence']:.2%}")
    
    # STEP 2: Handle Emergency Cases
    if symptom_result["emergency_flag"]:
        print("\n[ALERT] EMERGENCY DETECTED - SKIPPING OTHER AGENTS")
        
        emergency_output = OrchestratorOutput(
            recommendation="IMMEDIATE EMERGENCY RESPONSE REQUIRED",
            urgency=symptom_result["urgency"],
            emergency_flag=True,
            specialty=symptom_result["specialty"],
            hospitals=[],  # No time for hospital search
            cost_estimate="N/A - Emergency",
            guidance="Call emergency services (ambulance) immediately. " + 
                    "Inform them of: " + ", ".join(symptom_result["key_findings"]),
            confidence_score=symptom_result["confidence"]
        )
        
        print(f"\n✓ Emergency output generated")
        return emergency_output
    
    # STEP 3: Call Hospital Recommender Agent
    print("\n[STEP 2] Calling Hospital Recommender Agent...")
    try:
        hospital_result = call_hospital_recommender_agent(
            specialty=symptom_result["specialty"],
            location=location,
            urgency=symptom_result["urgency"]
        )
        print(f"✓ Hospital recommendations received")
        print(f"  - Hospitals found: {len(hospital_result.get('hospitals', []))}")
    except Exception as e:
        print(f"✗ Hospital agent error: {e}")
        hospital_result = {
            "hospitals": [],
            "guidance": "Unable to fetch hospital recommendations",
            "confidence": 0.0
        }
    
    # STEP 4: Call Cost Estimator Agent
    print("\n[STEP 3] Calling Cost Estimator Agent...")
    try:
        cost_result = call_cost_estimator_agent(
            specialty=symptom_result["specialty"],
            urgency=symptom_result["urgency"],
            location=location
        )
        print(f"✓ Cost estimation received")
        print(f"  - Estimate: {cost_result.get('estimate', 'N/A')}")
    except Exception as e:
        print(f"✗ Cost agent error: {e}")
        cost_result = {
            "estimate": "N/A",
            "confidence": 0.0,
            "breakdown": {}
        }
    
    # STEP 5: Aggregate Results
    print("\n[STEP 4] Aggregating Results...")
    
    guidance = f"""
Based on your symptoms, we recommend:

1. **Specialty**: {symptom_result['specialty']}
   - Reason: {symptom_result['reasoning']}

2. **Urgency Level**: {symptom_result['urgency'].upper()}
   - Key findings: {', '.join(symptom_result['key_findings'])}

3. **Next Steps**:
   {chr(10).join(f'   - {step}' for step in symptom_result['recommended_next_steps'])}

4. **Hospital Options**:
   {hospital_result.get('guidance', 'Hospitals recommendations')}

5. **Cost Estimate**:
   {cost_result.get('estimate', 'Cost estimates available at hospital')}

**Important**: This is guidance only, not a diagnosis.
Always consult healthcare professionals for definitive diagnosis and treatment.
""".strip()
    
    # Calculate overall confidence
    overall_confidence = (
        symptom_result["confidence"] * 0.5 +  # Symptom analysis
        hospital_result.get("confidence", 0.5) * 0.25 +  # Hospital data
        cost_result.get("confidence", 0.5) * 0.25  # Cost data
    )
    
    # Build final output
    final_output = OrchestratorOutput(
        recommendation=f"{symptom_result['specialty']} consultation recommended. Urgency: {symptom_result['urgency'].upper()}",
        urgency=symptom_result["urgency"],
        emergency_flag=False,
        specialty=symptom_result["specialty"],
        hospitals=hospital_result.get("hospitals", []),
        cost_estimate=cost_result.get("estimate", "N/A"),
        guidance=guidance,
        confidence_score=overall_confidence
    )
    
    print(f"\n✓ Results aggregated")
    print(f"  - Overall confidence: {overall_confidence:.2%}")
    
    # STEP 6: Validation
    print("\n[STEP 5] Validating Output...")
    required_fields = [
        "recommendation", "urgency", "emergency_flag", "specialty",
        "hospitals", "cost_estimate", "guidance", "confidence_score"
    ]
    missing = [f for f in required_fields if f not in final_output]
    if missing:
        print(f"✗ Missing fields: {missing}")
    else:
        print(f"✓ All required fields present")
    
    return final_output

# ============================================================================
# TESTING
# ============================================================================

async def test_orchestrator():
    """Test the orchestrator with sample cases"""
    
    test_cases = [
        {
            "name": "Emergency Case",
            "symptoms": "Chest pain and difficulty breathing for 30 minutes",
            "location": "Mumbai"
        },
        {
            "name": "General Case",
            "symptoms": "Persistent cough for 1 week, mild fever",
            "location": "Bangalore"
        },
        {
            "name": "Dermatology Case",
            "symptoms": "Itchy red rash on arms and legs",
            "location": "Delhi"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n\n{'#'*60}")
        print(f"# TEST: {test_case['name']}")
        print(f"{'#'*60}")
        
        result = await healthcare_orchestrator(
            symptoms=test_case["symptoms"],
            location=test_case["location"]
        )
        
        print(f"\n{'='*60}")
        print("FINAL OUTPUT:")
        print(f"{'='*60}")
        print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    # Run tests
    asyncio.run(test_orchestrator())
