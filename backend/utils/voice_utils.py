"""
UTILITY FUNCTIONS

Pure functions for:
- Speech-to-Text (STT) - Groq Whisper
- Text-to-Speech (TTS) - gTTS
- Image encoding
- Image validation and quality checks

These are backend utilities that support the voice interface.
NOT agents - just helper functions.
"""

import logging
import os
from groq import Groq
from gtts import gTTS
import base64
from PIL import Image
import cv2
import numpy as np

logger = logging.getLogger(__name__)

# ============================================================================
# SPEECH-TO-TEXT (STT)
# ============================================================================

def transcribe_with_groq(
    audio_filepath: str,
    GROQ_API_KEY: str = None,
    stt_model: str = "whisper-large-v3"
) -> str:
    """
    Convert audio to text using Groq Whisper API
    
    Input:
        - audio_filepath: Path to MP3/WAV audio file
        - GROQ_API_KEY: API key (defaults to env var)
        - stt_model: Model name (whisper-large-v3 recommended)
    
    Output:
        - Transcribed text string
    
    Raises:
        - FileNotFoundError if audio file not found
        - Exception if API call fails
    """
    
    if not GROQ_API_KEY:
        GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not provided or set in environment")
    
    if not os.path.exists(audio_filepath):
        raise FileNotFoundError(f"Audio file not found: {audio_filepath}")
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        with open(audio_filepath, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=stt_model,
                file=audio_file,
                language="en"
            )
        
        text = transcription.text
        logger.info(f"STT successful: {len(text)} characters")
        return text
        
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise

# ============================================================================
# TEXT-TO-SPEECH (TTS)
# ============================================================================

def text_to_speech_with_gtts(
    input_text: str,
    output_filepath: str = "output.mp3",
    language: str = "en"
) -> str:
    """
    Convert text to speech using Google TTS (gTTS)
    
    Input:
        - input_text: Text to convert to speech
        - output_filepath: Where to save MP3 file
        - language: Language code (default: English)
    
    Output:
        - Path to saved MP3 file
    
    Notes:
        - Free, unlimited usage
        - Natural sounding voice
        - Returns filepath for UI to play
    """
    
    if not input_text:
        raise ValueError("Input text cannot be empty")
    
    try:
        audio_obj = gTTS(
            text=input_text,
            lang=language,
            slow=False
        )
        
        audio_obj.save(output_filepath)
        logger.info(f"TTS successful: saved to {output_filepath}")
        
        return output_filepath
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise

# ============================================================================
# IMAGE ENCODING
# ============================================================================

def encode_image_to_base64(image_path: str) -> str:
    """
    Convert image file to base64 string
    
    Input:
        - image_path: Path to image file
    
    Output:
        - Base64 encoded string
    
    Supported formats:
        - JPEG, PNG, GIF, WebP
    """
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    try:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            logger.info(f"Image encoded: {len(encoded)} characters")
            return encoded
    except Exception as e:
        logger.error(f"Image encoding error: {e}")
        raise

# ============================================================================
# BATCH PROCESSING (Optional, for testing)
# ============================================================================

def transcribe_batch(audio_files: list[str]) -> list[str]:
    """Transcribe multiple audio files"""
    results = []
    for audio_file in audio_files:
        try:
            text = transcribe_with_groq(audio_file)
            results.append(text)
        except Exception as e:
            logger.error(f"Failed to transcribe {audio_file}: {e}")
            results.append("")
    return results
# ============================================================================
# IMAGE VALIDATION
# ============================================================================

def check_image_blur(image_path: str, threshold: float = 100.0) -> dict:
    """
    Detect if image is blurred using Laplacian variance method
    
    Input:
        - image_path: Path to image file
        - threshold: Laplacian variance threshold (lower = blurrier)
    
    Output:
        - {
            "is_blurred": bool,
            "blur_score": float,
            "message": str
          }
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {
                "is_blurred": True,
                "blur_score": 0,
                "message": "Could not read image. Invalid format or corrupted file."
            }
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        is_blurred = blur_score < threshold
        
        message = "Image is blurred. Please reupload a clear image." if is_blurred else "Image clarity is good."
        
        return {
            "is_blurred": is_blurred,
            "blur_score": float(blur_score),
            "message": message
        }
    except Exception as e:
        logger.error(f"Blur detection error: {e}")
        return {
            "is_blurred": True,
            "blur_score": 0,
            "message": f"Error analyzing image clarity: {str(e)}"
        }

def validate_medical_image(image_path: str) -> dict:
    """
    Validate if image appears to be medical-related
    Checks: image size, format, basic content
    
    Input:
        - image_path: Path to image file
    
    Output:
        - {
            "is_valid": bool,
            "image_size": (width, height),
            "file_format": str,
            "message": str
          }
    """
    try:
        if not os.path.exists(image_path):
            return {
                "is_valid": False,
                "image_size": None,
                "file_format": None,
                "message": "Image file not found."
            }
        
        # Check file size (medical images usually > 50KB)
        file_size_kb = os.path.getsize(image_path) / 1024
        if file_size_kb < 20:
            return {
                "is_valid": False,
                "image_size": None,
                "file_format": None,
                "message": "Image is too small. Please upload a higher quality medical image."
            }
        
        # Open and check image
        img = Image.open(image_path)
        width, height = img.size
        file_format = img.format
        
        # Check minimum dimensions (medical images are usually decent size)
        if width < 100 or height < 100:
            return {
                "is_valid": False,
                "image_size": (width, height),
                "file_format": file_format,
                "message": f"Image resolution too low ({width}x{height}). Please upload a higher resolution image."
            }
        
        # Check if it's a valid medical-related format
        valid_formats = ['JPEG', 'PNG', 'BMP', 'GIF']
        if file_format not in valid_formats:
            return {
                "is_valid": False,
                "image_size": (width, height),
                "file_format": file_format,
                "message": f"Invalid format: {file_format}. Please upload JPEG, PNG, or BMP images."
            }
        
        return {
            "is_valid": True,
            "image_size": (width, height),
            "file_format": file_format,
            "message": "Image format validated successfully."
        }
    except Exception as e:
        logger.error(f"Image validation error: {e}")
        return {
            "is_valid": False,
            "image_size": None,
            "file_format": None,
            "message": f"Could not validate image: {str(e)}"
        }

def validate_image_before_analysis(image_path: str) -> tuple[bool, str]:
    """
    Complete image validation pipeline
    
    Returns:
        - (is_valid, error_message)
        - If valid: (True, "")
        - If invalid: (False, "error message")
    """
    # Check basic file validity
    basic_validation = validate_medical_image(image_path)
    if not basic_validation["is_valid"]:
        return False, basic_validation["message"]
    
    # Check for blur
    blur_check = check_image_blur(image_path)
    if blur_check["is_blurred"]:
        return False, blur_check["message"]
    
    return True, ""