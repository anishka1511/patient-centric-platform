from fastapi import APIRouter
import sys
from pathlib import Path

# Add parent directory to path to import data_loader
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data_loader import generate_recommendation_response

# Create router
router = APIRouter()


@router.post("/recommend")
def recommend(request_body: dict):
    """
    Endpoint to get doctor recommendations based on specialty and location.
    
    Request body should contain:
    {
        "specialty": str,
        "location": str,
        "top_k": int (optional, default: 5)
    }
    
    Returns:
        dict: Recommendation response with metadata, doctor list, and cost summary
    """
    try:
        # Call the recommendation engine
        response = generate_recommendation_response(request_body)
        return response
    
    except Exception as e:
        # Handle any unexpected errors safely
        return {"error": "Internal server error."}

