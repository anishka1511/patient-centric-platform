"""
Interactive Test - Try Your Own Inputs
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.agent_orchestrator import agent_orchestrator
from services.conversation_service import conversation_service
from config.database import SessionLocal
from models.message import MessageRole
from datetime import datetime

print("="*70)
print("INTERACTIVE SYMPTOM ASSESSMENT TEST")
print("="*70)
print("Test different types of input:")
print("  - Greetings: 'hi', 'hello'")
print("  - Vague: 'pain', 'not feeling well'")
print("  - Emergency: 'chest pain', 'can't breathe'")
print("  - Dermatology: 'cherry angioma', 'face pimple'")
print("  - Valid: 'headache for 3 days', 'fever with cough'")
print("\nNote: Location is auto-detected (default: Mumbai for localhost)")
print("Note: Conversation history is maintained across messages in this session")
print("Type 'quit' to exit\n")
print("="*70)

session_id = f"test_session_{datetime.now().timestamp()}"
db = SessionLocal()

try:
    # Create conversation
    conversation = conversation_service.get_or_create_conversation(db, session_id)

    while True:
        try:
            user_input = input("\nYour input: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nExiting. Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Save user message
            conversation_service.add_message(
                db,
                conversation.id,
                MessageRole.USER,
                user_input
            )
            
            # Process through orchestrator with db for conversation history
            result = agent_orchestrator.assess_user_input(
                user_input, 
                session_id=session_id,
                db=db
            )
            
            print("\n" + "-"*70)
            print("RESULT:")
            print("-"*70)
            
            # Display based on response type
            if "category" in result:
                # Category response (IRRELEVANT or INSUFFICIENT_INFO)
                print(f"Category: {result['category']}")
                print(f"Message: {result.get('message', '')}")
                
                if "clarifying_questions" in result:
                    print("\nClarifying Questions:")
                    for q in result['clarifying_questions']:
                        print(f"  - {q}")
                
                if "suggestions" in result and result['suggestions']:
                    print("\nSuggestions:")
                    for s in result['suggestions']:
                        print(f"  - {s}")
            
            else:
                # Medical assessment response
                print(f"Symptoms: {', '.join(result.get('symptoms_identified', []))}")
                print(f"Urgency: {result.get('urgency_level', 'unknown').upper()}")
                print(f"Emergency: {'YES' if result.get('emergency_flag') else 'NO'}")
                print(f"Specialty: {result.get('recommended_specialty', 'N/A')}")
                print(f"Care Setting: {result.get('care_setting', 'N/A')}")
                
                if result.get('reasoning'):
                    print(f"\nReasoning: {result['reasoning']}")
                
                if result.get('safety_advice'):
                    print(f"\n⚠️  SAFETY ADVICE: {result['safety_advice']}")
            
            # Show location if detected
            if result.get('user_location'):
                loc = result['user_location']
                source = loc.get('source', 'unknown')
                print(f"\n📍 Location: {loc.get('city', 'Unknown')}, {loc.get('state', '')} ({source})")
            
            print("-"*70)
            
        except KeyboardInterrupt:
            print("\n\nExiting. Goodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()

finally:
    db.close()
    print("\nDatabase connection closed.")
