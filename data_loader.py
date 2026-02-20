import pandas as pd
from pathlib import Path
import json

# Module-level cache to ensure file loads only once
_cached_data = None

# Default number of recommendations to return
DEFAULT_TOP_K = 10

# Ordered nearby fallback map (lowercase keys/values)
NEARBY_MAP = {
    "akurdi": ["nigdi-pradhikaran", "pimpri-chinchwad", "ravet", "thergaon"],
    "alandi road": ["vishrantwadi", "dhanori", "yerwada", "lohegaon"],
    "amnora park town": ["hadapsar", "magarpatta city", "sasanenagar", "kharadi"],
    "anandnagar": ["sinhagad road", "vadgaon budruk", "manik bag", "hingne"],
    "aundh": ["baner", "pashan", "wakad", "balewadi", "pimple nilakh"],
    "balewadi": ["baner", "wakad", "aundh", "mahalunge", "pimple nilakh"],
    "baner": ["baner road", "aundh", "balewadi", "pashan", "wakad", "mahalunge"],
    "baner pashan link road": ["baner", "pashan", "balewadi"],
    "baner road": ["baner", "aundh", "balewadi"],
    "bavdhan": ["kothrud", "warje", "paud road", "pashan"],
    "bhosari": ["moshi", "pimpri-chinchwad", "chikhali", "dhanori"],
    "bibvewadi": ["market yard", "dhankawadi", "parvati gaon", "kondhwa"],
    "bibwewadi kondhwa road": ["bibvewadi", "kondhwa", "market yard"],
    "budhwar peth": ["shaniwar peth", "kasba peth", "sadashiv peth", "camp"],
    "camp": ["wanowrie", "wanwadi", "koregaon park", "kasba peth"],
    "chikhali": ["moshi", "bhosari", "talawade"],
    "deccan gymkhana": ["fc road", "jm road", "erandwane", "shivajinagar"],
    "dhankawadi": ["katraj", "bibvewadi", "parvati gaon"],
    "dhanori": ["vishrantwadi", "lohegaon", "yerwada", "bhosari"],
    "erandwane": ["kothrud", "deccan gymkhana", "karve nagar", "law college road"],
    "fc road": ["jm road", "deccan gymkhana", "shivajinagar"],
    "hadapsar": ["magarpatta city", "kharadi", "sasanenagar", "wanowrie"],
    "hinjewadi": ["wakad", "mahalunge", "marunji"],
    "jm road": ["fc road", "shivajinagar", "deccan gymkhana"],
    "junnar": [],
    "kalyani nagar": ["viman nagar", "yerwada", "wadgaon sheri", "koregaon park"],
    "karve nagar": ["kothrud", "warje", "erandwane"],
    "kasba peth": ["budhwar peth", "shaniwar peth", "camp"],
    "katraj": ["dhankawadi", "ambegaon", "parvati gaon"],
    "keshav nagar": ["mundhwa", "kharadi", "magarpatta city"],
    "kharadi": ["viman nagar", "hadapsar", "wagholi", "magarpatta city", "keshav nagar"],
    "kondhwa": ["bibvewadi", "nibm", "mohamadwadi", "lulla nagar"],
    "koregaon park": ["kalyani nagar", "yerwada", "camp"],
    "kothrud": ["karve nagar", "paud road", "warje", "shivajinagar", "bavdhan"],
    "law college road": ["erandwane", "prabhat road", "deccan gymkhana"],
    "lohegaon": ["viman nagar", "dhanori", "wagholi"],
    "lonavala": [],
    "lulla nagar": ["wanowrie", "kondhwa", "salunke vihar"],
    "magarpatta city": ["hadapsar", "kharadi", "amanora park town"],
    "mahalunge": ["balewadi", "baner", "hinjewadi"],
    "market yard": ["bibvewadi", "swargate", "mukund nagar"],
    "model colony": ["shivajinagar", "senapati bapat marg", "jm road"],
    "mohamadwadi": ["kondhwa", "undri", "nibm"],
    "moshi": ["bhosari", "chikhali", "pimpri-chinchwad"],
    "mukund nagar": ["swargate", "market yard", "parvati gaon"],
    "nagar road": ["kalyani nagar", "viman nagar", "yerwada"],
    "nanded city": ["sinhagad road", "vadgaon budruk"],
    "navi peth": ["sadashiv peth", "shaniwar peth"],
    "nibm": ["kondhwa", "undri", "wanowrie"],
    "nigdi-pradhikaran": ["akurdi", "ravet", "pimpri-chinchwad"],
    "parvati gaon": ["dhankawadi", "mukund nagar", "bibvewadi"],
    "pashan": ["baner", "aundh", "bavdhan"],
    "paud road": ["kothrud", "warje", "bavdhan"],
    "pimple nilakh": ["wakad", "aundh", "balewadi", "pimple saudagar"],
    "pimple saudagar": ["wakad", "pimple nilakh", "thergaon"],
    "pimpri-chinchwad": ["akurdi", "bhosari", "thergaon", "ravet"],
    "porwal road": ["lohegaon", "dhanori"],
    "prabhat road": ["law college road", "deccan gymkhana"],
    "ravet": ["akurdi", "nigdi-pradhikaran", "thergaon"],
    "sadashiv peth": ["budhwar peth", "shaniwar peth", "navi peth"],
    "salunke vihar": ["wanowrie", "lulla nagar", "kondhwa"],
    "sasanenagar": ["hadapsar", "magarpatta city"],
    "senapati bapat marg": ["model colony", "shivajinagar"],
    "shaniwar peth": ["budhwar peth", "sadashiv peth", "kasba peth"],
    "shankar shet road": ["swargate", "mukund nagar"],
    "shivajinagar": ["deccan gymkhana", "model colony", "fc road", "kothrud"],
    "sinhagad road": ["vadgaon budruk", "anandnagar", "nanded city"],
    "sopan baug": ["wanowrie", "koregaon park"],
    "swargate": ["market yard", "mukund nagar", "shankar shet road"],
    "thergaon": ["wakad", "ravet", "pimpri-chinchwad"],
    "undri": ["kondhwa", "mohamadwadi", "nibm"],
    "vadgaon budruk": ["sinhagad road", "nanded city"],
    "viman nagar": ["kalyani nagar", "kharadi", "lohegaon", "yerwada"],
    "vishrantwadi": ["dhanori", "yerwada", "alandi road"],
    "wadgaon sheri": ["kalyani nagar", "viman nagar", "kharadi"],
    "wagholi": ["kharadi", "lohegaon"],
    "wakad": ["hinjewadi", "baner", "balewadi", "pimpri-chinchwad", "pimple nilakh"],
    "wanowrie": ["wanwadi", "camp", "lulla nagar", "sopan baug"],
    "wanwadi": ["wanowrie", "camp", "salunke vihar"],
    "warje": ["kothrud", "karve nagar", "paud road"],
    "yerwada": ["kalyani nagar", "viman nagar", "dhanori"],
}


# Location coordinates map (lowercase keys)
LOCATION_COORDS = {
    "baner": (18.5590, 73.7890),
    "baner road": (18.5594, 73.7876),
    "aundh": (18.5604, 73.8071),
    "balewadi": (18.5689, 73.7720),
    "pashan": (18.5354, 73.7850),
    "wakad": (18.5998, 73.7616),
    "hinjewadi": (18.5913, 73.7389),
    "pimpri-chinchwad": (18.6298, 73.7997),
    "kothrud": (18.5074, 73.8077),
    "karve nagar": (18.5024, 73.8166),
    "paud road": (18.5095, 73.7986),
    "warje": (18.4865, 73.8010),
    "shivajinagar": (18.5308, 73.8475),
    "kharadi": (18.5511, 73.9422),
    "viman nagar": (18.5679, 73.9154),
    "hadapsar": (18.5089, 73.9260),
    "wagholi": (18.5793, 73.9790),
    "magarpatta": (18.5167, 73.9346),
    "koregaon park": (18.5362, 73.8940),
    "fc road": (18.5196, 73.8409),
    "nibm": (18.4590, 73.8966),
    "swargate": (18.5018, 73.8636),
}


def validate_location_coordinates():
    """
    Validate LOCATION_COORDS structure and coordinate ranges.
    """
    invalid_keys = [key for key in LOCATION_COORDS.keys() if key != key.lower()]
    if invalid_keys:
        raise ValueError(f"LOCATION_COORDS contains non-lowercase keys: {sorted(invalid_keys)}")

    invalid_coords = []
    for key, coords in LOCATION_COORDS.items():
        if not isinstance(coords, (tuple, list)) or len(coords) != 2:
            invalid_coords.append(key)
            continue
        lat, lon = coords
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            invalid_coords.append(key)

    if invalid_coords:
        raise ValueError(f"Invalid coordinates for locations: {sorted(invalid_coords)}")


# Validate coordinates once at initialization
validate_location_coordinates()


def _convert_to_json_serializable(value):
    """
    Convert numpy/pandas types to native Python types for JSON serialization.
    
    Args:
        value: Value to convert
    
    Returns:
        JSON-serializable value
    """
    if value is None:
        return None
    
    # Convert numpy types to Python native types
    if hasattr(value, 'item'):  # numpy scalar
        return value.item()
    
    return value


def load_doctors_data():
    """
    Load and clean the doctors data from CSV file.
    
    Returns:
        pd.DataFrame: Cleaned DataFrame with standardized column names.
        
    Raises:
        FileNotFoundError: If the CSV file is not found.
    """
    global _cached_data
    
    # Return cached data if already loaded
    if _cached_data is not None:
        return _cached_data
    
    file_path = Path("data/doctors.csv")
    
    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path.absolute()}")
    
    try:
        # Load the CSV file
        df = pd.read_csv(file_path)
        
        # Map raw column names to standardized names
        column_mapping = {
            'doctors_name': 'name',
            'doctors_profession': 'specialty',
            'doctors_location': 'location',
            'consultation_fee': 'consultation_fee',
            'rating_score': 'rating_score'
        }
        
        # Rename columns to standardized names
        df = df.rename(columns=column_mapping)
        
        # Drop rows where consultation_fee or rating_score is null
        df = df.dropna(subset=['consultation_fee', 'rating_score'])
        
        # Select only standardized columns
        df = df[['name', 'specialty', 'location', 'consultation_fee', 'rating_score']]
        
        # Clean location column: strip whitespace, remove trailing commas, convert to lowercase
        df['location'] = df['location'].str.strip().str.rstrip(',').str.lower()

        # Validate LOCATION_COORDS covers all dataset locations
        dataset_locations = set(df['location'].dropna().unique())
        coords_locations = set(LOCATION_COORDS.keys())
        missing_locations = sorted(dataset_locations - coords_locations)
        if missing_locations:
            raise ValueError(
                f"Missing LOCATION_COORDS for locations: {missing_locations}"
            )
        
        # Cache the cleaned data
        _cached_data = df
        
        return _cached_data
    
    except Exception as e:
        raise Exception(f"Error loading doctors data: {str(e)}")


def _compute_cost_score(fees):
    """
    Compute cost score from consultation fees.
    Lower fees receive higher scores.
    
    Args:
        fees (pd.Series): Series of consultation fees.
    
    Returns:
        pd.Series: Cost scores normalized between 0 and 1.
    """
    min_fee = fees.min()
    max_fee = fees.max()
    
    if max_fee == min_fee:
        return pd.Series(1.0, index=fees.index)
    
    return 1 - (fees - min_fee) / (max_fee - min_fee)


def _compute_location_score(locations, user_location):
    """
    Compute location score based on matching user's preferred location.
    
    Args:
        locations (pd.Series): Series of doctor locations.
        user_location (str): User's preferred location.
    
    Returns:
        pd.Series: Location scores (1.0 for match, 0.5 otherwise).
    """
    return locations.str.lower().eq(user_location.lower()).astype(float).where(
        locations.str.lower().eq(user_location.lower()), 0.5
    )


def _generate_reason(rating_score, consultation_fee, location_score, percentile_25):
    """
    Generate a reason/explanation string for a doctor recommendation.
    
    Args:
        rating_score (float): Doctor's rating score (0-1)
        consultation_fee (float): Doctor's consultation fee
        location_score (float): Location match score (1.0 or 0.5)
        percentile_25 (float): 25th percentile of consultation fees in filtered group
    
    Returns:
        str: Reason string combining applicable tags
    """
    reasons = []
    
    # Check if highly rated
    if rating_score >= 0.9:
        reasons.append("Highly rated")
    
    # Check if affordable (within bottom 25%)
    if consultation_fee <= percentile_25:
        reasons.append("Affordable")
    
    # Check if nearby
    if location_score == 1.0:
        reasons.append("Nearby")
    
    # Return combined reason or default
    return " • ".join(reasons) if reasons else "Balanced recommendation"


def rank_doctors(df, user_location, top_k=5):
    """
    Rank doctors based on a weighted scoring system.
    
    Args:
        df (pd.DataFrame): DataFrame containing doctor data with columns:
            name, specialty, location, consultation_fee, rating_score.
        user_location (str): User's preferred location.
        top_k (int): Number of top results to return. Default is 5.
    
    Returns:
        list: List of dictionaries with top_k doctors sorted by final_score.
              Each dict contains: name, specialty, location, 
              consultation_fee, rating_score, final_score, reason.
    """
    # Validate required columns
    required_columns = {'name', 'specialty', 'location', 'consultation_fee', 'rating_score'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")
    
    # Create a copy to avoid modifying original data
    df = df.copy()
    
    # Compute scores
    df['cost_score'] = _compute_cost_score(df['consultation_fee'])
    df['location_score'] = _compute_location_score(df['location'], user_location)
    
    # Compute final score: 0.5 * rating + 0.3 * cost + 0.2 * location
    df['final_score'] = (
        0.5 * df['rating_score'] +
        0.3 * df['cost_score'] +
        0.2 * df['location_score']
    )
    
    # Calculate 25th percentile of consultation fees for "Affordable" tag
    percentile_25 = df['consultation_fee'].quantile(0.25)
    
    # Get top_k doctors sorted by final_score descending
    top_doctors = df.nlargest(top_k, 'final_score')
    
    # Format results as list of dictionaries
    results = []
    for _, row in top_doctors.iterrows():
        location_key = str(row['location']).strip().lower()
        coords = LOCATION_COORDS.get(location_key)
        latitude = float(coords[0]) if coords else None
        longitude = float(coords[1]) if coords else None
        # Generate reason string
        reason = _generate_reason(
            rating_score=float(_convert_to_json_serializable(row['rating_score'])),
            consultation_fee=float(_convert_to_json_serializable(row['consultation_fee'])),
            location_score=float(_convert_to_json_serializable(row['location_score'])),
            percentile_25=float(percentile_25)
        )
        
        results.append({
            'name': row['name'],
            'specialty': row['specialty'],
            'location': row['location'],
            'consultation_fee': int(_convert_to_json_serializable(row['consultation_fee'])),
            'rating_score': round(float(_convert_to_json_serializable(row['rating_score'])), 2),
            'final_score': round(float(_convert_to_json_serializable(row['final_score'])), 4),
            'reason': reason,
            'latitude': latitude,
            'longitude': longitude
        })
    
    return results


def recommend_doctors(input_data: dict):
    """
    Recommend doctors based on specialty and location preferences.
    
    Args:
        input_data (dict): Dictionary containing:
            - "specialty" (str): Desired medical specialty
            - "location" (str): Preferred location
    
    Returns:
        dict: Dictionary with keys:
            - "recommended_doctors": List of recommended doctor dicts
            - "total_matches": Total doctors matching the specialty
            - "message": Optional message if no matches found
    """
    # Extract parameters
    specialty = input_data.get("specialty", "").strip().lower()
    location = input_data.get("location", "").strip().lower()
    
    # Validate inputs
    if not specialty or not location:
        raise ValueError("Both 'specialty' and 'location' are required.")
    
    # Load dataset
    df = load_doctors_data()
    
    # Filter by specialty (case insensitive)
    filtered_df = df[df['specialty'].str.lower() == specialty]

    fallback_applied = False
    fallback_location = None
    fallback_type = None
    original_specialty = specialty

    # First attempt: exact location match
    location_filtered = filtered_df[filtered_df['location'].str.lower() == location]

    # If no exact results, try nearby locations in order
    if location_filtered.empty:
        nearby_locations = NEARBY_MAP.get(location, [])
        for nearby in nearby_locations:
            nearby_filtered = filtered_df[filtered_df['location'].str.lower() == nearby]
            if not nearby_filtered.empty:
                location_filtered = nearby_filtered
                fallback_applied = True
                fallback_location = nearby
                fallback_type = "nearby"
                break
    
    # Final tier: fallback to general physician in original location
    if location_filtered.empty:
        gp_filtered = df[
            (df['specialty'].str.lower() == "general_physician") &
            (df['location'].str.lower() == location)
        ]
        if not gp_filtered.empty:
            location_filtered = gp_filtered
            fallback_applied = True
            fallback_type = "general_physician"

    filtered_df = location_filtered
    
    # Handle no matches
    if filtered_df.empty:
        return {
            "recommended_doctors": [],
            "total_matches": 0,
            "message": "No doctors found for this specialty or fallback.",
            "metadata": {
                "fallback_applied": False,
                "fallback_location": None,
                "fallback_type": None,
                "original_specialty": original_specialty
            }
        }
    
    # Get total matches before trimming
    total_matches = len(filtered_df)
    
    # Rank doctors
    recommended = rank_doctors(filtered_df, location, top_k=DEFAULT_TOP_K)
    
    # Return structured response
    return {
        "recommended_doctors": recommended,
        "total_matches": total_matches,
        "metadata": {
            "fallback_applied": fallback_applied,
            "fallback_location": fallback_location,
            "fallback_type": fallback_type,
            "original_specialty": original_specialty
        }
    }


def generate_cost_insights(input_data: dict):
    """
    Generate cost insights for doctors matching specialty and location.
    
    Args:
        input_data (dict): Dictionary containing:
            - "specialty" (str): Desired medical specialty
            - "location" (str): Preferred location
    
    Returns:
        dict: Dictionary with keys:
            - "average_fee": Average consultation fee (rounded to 2 decimals)
            - "min_fee": Minimum consultation fee
            - "max_fee": Maximum consultation fee
            - "cost_band": Cost category ("Budget-friendly", "Standard", or "Premium")
            - "message": Optional message if no data found
    """
    # Extract parameters
    specialty = input_data.get("specialty", "").strip()
    location = input_data.get("location", "").strip()
    
    # Validate inputs
    if not specialty or not location:
        raise ValueError("Both 'specialty' and 'location' are required.")
    
    # Load dataset
    df = load_doctors_data()
    
    # Filter by specialty (case insensitive)
    filtered_df = df[df['specialty'].str.lower() == specialty.lower()]
    
    # Further filter by location (case insensitive)
    filtered_df = filtered_df[filtered_df['location'].str.lower() == location.lower()]
    
    # Handle no matches
    if filtered_df.empty:
        return {
            "average_fee": None,
            "min_fee": None,
            "max_fee": None,
            "cost_band": None,
            "message": "No cost data available for this selection."
        }
    
    # Compute fee statistics and convert to native Python types
    average_fee = float(round(float(_convert_to_json_serializable(filtered_df['consultation_fee'].mean())), 2))
    min_fee = float(round(float(_convert_to_json_serializable(filtered_df['consultation_fee'].min())), 2))
    max_fee = float(round(float(_convert_to_json_serializable(filtered_df['consultation_fee'].max())), 2))
    
    # Determine cost band
    if average_fee < 300:
        cost_band = "Budget-friendly"
    elif average_fee <= 500:
        cost_band = "Standard"
    else:
        cost_band = "Premium"
    
    # Return structured response
    return {
        "average_fee": average_fee,
        "min_fee": min_fee,
        "max_fee": max_fee,
        "cost_band": cost_band
    }


def generate_recommendation_response(input_data: dict):
    """
    Generate a comprehensive recommendation response combining doctor recommendations
    and cost insights.
    
    Args:
        input_data (dict): Dictionary containing:
            - "specialty" (str): Desired medical specialty
            - "location" (str): Preferred location
    
    Returns:
        dict: Dictionary with keys:
            - "metadata": Query and fallback information
            - "recommended_doctors": List of recommended doctor dicts
            - "cost_summary": Dict with average_fee, min_fee, max_fee, cost_band
            - "message": Optional message if no doctors found
            - "error": Error message if validation fails
    """
    # Validate input is a dictionary
    if not isinstance(input_data, dict):
        return {"error": "Invalid input format."}
    
    # Extract and validate specialty
    specialty = input_data.get("specialty", "").strip().lower()
    if not specialty:
        return {"error": "Specialty is required."}
    
    # Extract and validate location
    location = input_data.get("location", "").strip().lower()
    if not location:
        return {"error": "Location is required."}
    
    # Prepare cleaned input for processing
    cleaned_input = {
        "specialty": specialty,
        "location": location
    }
    
    # Get doctor recommendations
    recommendations = recommend_doctors(cleaned_input)
    
    # Get cost insights
    cost_insights = generate_cost_insights(cleaned_input)
    
    # Extract returned count and total matches
    returned_count = len(recommendations.get("recommended_doctors", []))
    total_matches = recommendations.get("total_matches", 0)
    fallback_metadata = recommendations.get("metadata", {})
    fallback_type = fallback_metadata.get("fallback_type")
    
    # Build metadata with simplified fields
    metadata = {
        "query_specialty": specialty,
        "query_location": location,
        "total_doctors_available": total_matches,
        "returned_count": returned_count,
        "fallback_applied": fallback_metadata.get("fallback_applied", False),
        "fallback_location": fallback_metadata.get("fallback_location"),
        "fallback_type": fallback_type
    }
    
    # Include original_specialty only when fallback_type is general_physician
    if fallback_type == "general_physician":
        metadata["original_specialty"] = fallback_metadata.get("original_specialty", specialty)
    
    # Build response structure
    response = {
        "metadata": metadata,
        "recommended_doctors": recommendations.get("recommended_doctors", []),
        "cost_summary": {
            "average_fee": cost_insights.get("average_fee"),
            "min_fee": cost_insights.get("min_fee"),
            "max_fee": cost_insights.get("max_fee"),
            "cost_band": cost_insights.get("cost_band")
        }
    }
    
    # Include message if present
    if "message" in recommendations:
        response["message"] = recommendations["message"]
    
    return response
