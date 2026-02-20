# if you dont use pipenv uncomment the following:
from dotenv import load_dotenv
load_dotenv()

#VoiceBot UI with Gradio
import os
import json
import gradio as gr

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import record_audio, transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts, text_to_speech_with_elevenlabs
from backend.agents.symptom_agent import symptom_analysis_agent
from backend.utils.voice_utils import validate_image_before_analysis

image_prompt="""You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""

def is_minimal_symptom(symptom_text: str) -> bool:
    """Check if symptom description is too brief (needs more detail)"""
    # Less than 3 words or very short = minimal
    word_count = len(symptom_text.split())
    return word_count < 5

def process_inputs(audio_filepath, image_filepath):
    try:
        # Transcribe audio
        speech_to_text_output = transcribe_with_groq(GROQ_API_KEY=os.environ.get("GROQ_API_KEY"), 
                                                     audio_filepath=audio_filepath,
                                                     stt_model="whisper-large-v3")

        # Handle with or without image
        if image_filepath:
            try:
                # Validate image before processing
                is_valid, error_message = validate_image_before_analysis(image_filepath)
                
                if not is_valid:
                    # Image is invalid (blurred, wrong format, etc.)
                    doctor_response = f"""RESULT: - 
Symptoms: {speech_to_text_output}
Urgency: N/A
Emergency: NO
Specialty: N/A
Care Setting: N/A
Reasoning: Invalid Image - {error_message}

⚠️ IMAGE ERROR: {error_message}

Please reupload a clear, high-resolution medical image for accurate analysis."""
                else:
                    # Image is valid: use multimodal analysis (image + symptoms)
                    doctor_response = analyze_image_with_query(
                        query=image_prompt + speech_to_text_output, 
                        encoded_image=encode_image(image_filepath), 
                        model="meta-llama/llama-4-scout-17b-16e-instruct"
                    )
            except Exception as e:
                doctor_response = f"""RESULT: - 
Symptoms: {speech_to_text_output}
Urgency: N/A
Emergency: NO
Specialty: N/A
Care Setting: N/A
Reasoning: Error processing image

⚠️ IMAGE PROCESSING ERROR: {str(e)}

Please try again or use audio-only mode."""
        else:
            # If no image: use symptom agent to analyze symptoms only
            try:
                symptom_result = symptom_analysis_agent(symptoms=speech_to_text_output)
                
                # Format the response according to user's desired format
                emergency_status = "YES" if symptom_result.get('emergency_flag') else "NO"
                urgency_level = symptom_result['urgency'].upper()
                
                # Get specialty as string (handle enum if needed)
                specialty = str(symptom_result['specialty']).replace('MedicalSpecialty.', '')
                
                # Determine care setting based on urgency
                care_setting = {
                    'CRITICAL': 'Emergency Department',
                    'HIGH': 'Urgent Care',
                    'MEDIUM': 'clinic',
                    'LOW': 'clinic'
                }.get(urgency_level, 'clinic')
                
                doctor_response = f"""RESULT: - 
Symptoms: {speech_to_text_output}
Urgency: {urgency_level}
Emergency: {emergency_status}
Specialty: {specialty}
Care Setting: {care_setting}
Reasoning: {symptom_result['reasoning']}
your location: longitude latitude"""
                
                # If symptoms are minimal, add guidance to provide more details
                if is_minimal_symptom(speech_to_text_output):
                    doctor_response += f"""

ℹ️ NOTE: For more accurate diagnosis, please provide more details:
- How long have you had these symptoms?
- What is the severity (mild/moderate/severe)?
- Any other associated symptoms?
- Any recent injuries or medical history?
- Current medications?

A detailed symptom description will help provide better medical guidance."""
            except Exception as e:
                doctor_response = f"""RESULT: - 
Symptoms: {speech_to_text_output}
Urgency: MEDIUM
Emergency: NO
Specialty: GENERAL
Care Setting: clinic
Reasoning: Error in analysis

⚠️ ANALYSIS ERROR: {str(e)}

Please try recording your symptoms again with more detail."""

        # Generate speech response
        try:
            voice_of_doctor = text_to_speech_with_gtts(input_text=doctor_response, output_filepath="final.mp3")
        except Exception as e:
            print(f"TTS Error: {e}")
            voice_of_doctor = "final.mp3"  # Return path even if TTS fails

        return speech_to_text_output, doctor_response, voice_of_doctor
    
    except Exception as e:
        error_response = f"""RESULT: - 
Symptoms: Error in recording
Urgency: N/A
Emergency: NO
Specialty: N/A
Care Setting: N/A
Reasoning: System error

⚠️ SYSTEM ERROR: {str(e)}

Please refresh the page and try again."""
        return "Error", error_response, "final.mp3"


# Create the interface
iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath", label="Record Your Symptoms"),
        gr.Image(type="filepath", label="Medical Image (Optional)")
    ],
    outputs=[
        gr.Textbox(label="Your Symptoms (Transcribed)"),
        gr.Textbox(label="Medical Assessment"),
        gr.Audio(label="Doctor's Voice Response")
    ],
    title="AI Doctor with Vision and Voice",
    description="Share your symptoms via microphone. Optionally upload a medical image for visual analysis."
)

iface.launch(debug=True)

#http://127.0.0.1:7860