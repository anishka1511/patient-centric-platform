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
    # Previously unmapped locations
    "bhugaon": ["bavdhan", "warje", "kothrud"],
    "bt kawade road": ["kharadi", "viman nagar", "wadgaon sheri"],
    "bund garden": ["koregaon park", "camp", "yerwada"],
    "chakan": ["moshi", "bhosari"],
    "chandan nagar": ["kharadi", "viman nagar", "wadgaon sheri"],
    "dapodi": ["khadki", "aundh", "pimpri-chinchwad"],
    "dhayari": ["sinhagad road", "warje", "kothrud"],
    "dhole patil road": ["camp", "koregaon park", "bund garden", "kasba peth", "rasta peth", "shivajinagar"],
    "ganga dham": ["market yard", "bibvewadi", "swargate"],
    "gultekdi": ["market yard", "swargate", "bibvewadi"],
    "khadki": ["dapodi", "aundh", "shivajinagar"],
    "magarpatta": ["hadapsar", "magarpatta city", "kharadi"],
    "manik bag": ["kothrud", "karve nagar", "erandwane"],
    "mangalvar peth": ["rasta peth", "kasba peth", "budhwar peth", "camp", "dhole patil road"],
    "marunji": ["hinjewadi", "mahalunge", "wakad"],
    "mohammadwadi": ["kondhwa", "undri", "nibm"],
    "mundhwa": ["keshav nagar", "kharadi", "hadapsar"],
    "narayan peth": ["sadashiv peth", "shaniwar peth", "budhwar peth"],
    "parvati paytha": ["parvati gaon", "swargate", "mukund nagar"],
    "rahatani": ["pimple saudagar", "thergaon", "wakad"],
    "rasta peth": ["kasba peth", "budhwar peth", "camp", "mangalvar peth"],
    "shukrawar peth": ["shaniwar peth", "budhwar peth", "sadashiv peth"],
    "tilak road": ["sadashiv peth", "shaniwar peth", "deccan gymkhana"],
}


# Location coordinates map (lowercase keys) - Real coordinates from OpenStreetMap Nominatim API
LOCATION_COORDS = {
    "akurdi": (18.6486, 73.7647),
    "alandi road": (18.5612, 73.8767),
    "amnora park town": (18.5167, 73.9346),
    "aundh": (18.5619, 73.8102),
    "balewadi": (18.582, 73.769),
    "baner": (18.5642, 73.7769),
    "baner road": (18.5647, 73.7748),
    "bavdhan": (18.521, 73.7781),
    "bhosari": (18.621, 73.8501),
    "bhugaon": (18.5, 73.7501),
    "bibvewadi": (18.4782, 73.8621),
    "bt kawade road": (18.5467, 73.8800),
    "budhwar peth": (18.5176, 73.858),
    "bund garden": (18.5406, 73.8834),
    "camp": (18.5216, 73.8718),
    "chakan": (18.7623, 73.8625),
    "chandan nagar": (18.5571, 73.9281),
    "chikhali": (18.6642, 73.8267),
    "dapodi": (18.5817, 73.8327),
    "deccan gymkhana": (18.5159, 73.8412),
    "dhankawadi": (18.4653, 73.855),
    "dhanori": (18.5907, 73.8913),
    "dhayari": (18.4374, 73.819),
    "dhole patil road": (18.5349, 73.8767),
    "erandwane": (18.5087, 73.8318),
    "fc road": (18.515, 73.8422),
    "ganga dham": (18.4793, 73.8754),
    "gultekdi": (18.4939, 73.8676),
    "hinjewadi": (18.592, 73.7579),
    "hadapsar": (18.5089, 73.9260),
    "jm road": (18.525, 73.8496),
    "junnar": (19.2007, 73.9768),
    "kalyani nagar": (18.5481, 73.9026),
    "karve nagar": (18.4894, 73.8213),
    "kasba peth": (18.5219, 73.8583),
    "katraj": (18.4537, 73.8563),
    "keshav nagar": (18.5323, 73.9384),
    "khadki": (18.5682, 73.8508),
    "kharadi": (18.5513, 73.9417),
    "kondhwa": (18.478, 73.8941),
    "koregaon park": (18.5366, 73.8933),
    "kothrud": (18.5071, 73.8051),
    "law college road": (18.5166, 73.8294),
    "lohegaon": (18.5804, 73.9182),
    "lonavala": (18.7504, 73.4069),
    "lulla nagar": (18.4590, 73.8966),
    "magarpatta": (18.5112, 73.9274),
    "magarpatta city": (18.5112, 73.9274),
    "mahalunge": (19.0931, 73.7527),
    "mangalvar peth": (18.5210, 73.8650),
    "manik bag": (18.5400, 73.8300),
    "market yard": (18.3367, 74.3814),
    "marunji": (18.6117, 73.7156),
    "model colony": (18.5314, 73.8375),
    "mohammadwadi": (18.4733, 73.9238),
    "mohamadwadi": (18.4733, 73.9238),
    "moshi": (18.6523, 73.8442),
    "mukund nagar": (18.4952, 73.8662),
    "mundhwa": (18.5343, 73.9298),
    "nagar road": (18.5629, 73.9301),
    "nanded city": (18.4597, 73.786),
    "narayan peth": (18.5156, 73.8511),
    "navi peth": (18.5093, 73.8441),
    "nibm": (18.4642, 73.9029),
    "nigdi-pradhikaran": (18.6559, 73.7681),
    "parvati gaon": (18.5018, 73.8636),
    "parvati paytha": (18.4985, 73.8497),
    "pashan": (18.5387, 73.7953),
    "paud road": (18.5076, 73.7792),
    "pimple nilakh": (18.5697, 73.7941),
    "pimple saudagar": (18.5982, 73.7978),
    "pimpri-chinchwad": (18.6279, 73.801),
    "porwal road": (18.6086, 73.9111),
    "prabhat road": (18.512, 73.8316),
    "rahatani": (18.6025, 73.796),
    "rasta peth": (18.5198, 73.865),
    "ravet": (18.6433, 73.7451),
    "sadashiv peth": (18.5108, 73.8502),
    "salunke vihar": (18.4590, 73.8966),
    "sasanenagar": (18.5167, 73.9346),
    "senapati bapat marg": (18.5242, 73.8297),
    "shaniwar peth": (18.5193, 73.8525),
    "shankar shet road": (18.4952, 73.8662),
    "shivajinagar": (18.5326, 73.8513),
    "shukrawar peth": (18.5114, 73.854),
    "sinhagad road": (18.5005, 73.8446),
    "sopan baug": (18.5142, 73.9014),
    "swargate": (18.4989, 73.8585),
    "thergaon": (18.6093, 73.7729),
    "tilak road": (18.5033, 73.8561),
    "undri": (18.4516, 73.8927),
    "vadgaon budruk": (18.4675, 73.8254),
    "viman nagar": (18.5704, 73.9133),
    "vishrantwadi": (18.5726, 73.8782),
    "wadgaon sheri": (18.5436, 73.9241),
    "wagholi": (18.5806, 73.9833),
    "wakad": (18.6022, 73.7644),
    "wanowrie": (18.4884, 73.8987),
    "wanwadi": (18.4884, 73.8987),
    "warje": (18.482, 73.8002),
    "yerwada": (18.5453, 73.8867),
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


def convert_coordinates_to_location(latitude: float, longitude: float, max_distance_km: float = 10.0) -> str:
    """
    Convert latitude/longitude coordinates to the nearest known location name.
    Uses Haversine formula to calculate distance between coordinates.
    
    Args:
        latitude (float): User's latitude coordinate
        longitude (float): User's longitude coordinate
        max_distance_km (float): Maximum distance in km to consider a match (default: 10km)
    
    Returns:
        str: Nearest location name (lowercase) or None if no location within max_distance
    
    Example:
        >>> convert_coordinates_to_location(18.5642, 73.7769)
        'baner'
    """
    from math import radians, sin, cos, sqrt, atan2
    
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates in kilometers."""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    # Find nearest location
    min_distance = float('inf')
    nearest_location = None
    
    for location_name, (loc_lat, loc_lon) in LOCATION_COORDS.items():
        distance = haversine_distance(latitude, longitude, loc_lat, loc_lon)
        if distance < min_distance:
            min_distance = distance
            nearest_location = location_name
    
    # Return location only if within max_distance threshold
    if min_distance <= max_distance_km:
        return nearest_location
    else:
        return None


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


def _get_valid_contact_number(contact_number):
    """
    Validate and clean contact_number for JSON serialization.
    
    Args:
        contact_number: Contact number from dataframe (can be str, None, NaN)
    
    Returns:
        str: Valid contact number string, or None if empty/invalid
    """
    if contact_number is None:
        return None
    
    # Convert to string and strip whitespace
    contact_str = str(contact_number).strip()
    
    # Return None if empty or represents missing value
    if not contact_str or contact_str.lower() in ['nan', 'none', '']:
        return None
    
    return contact_str


def load_doctors_data():
    """
    Load and clean the doctors data from CSV file.
    
    Preprocesses doctors_master_sheet.csv with column renaming, data type conversions,
    and cleaning operations.
    
    Returns:
        pd.DataFrame: Cleaned DataFrame with standardized column names and types.
        
    Raises:
        FileNotFoundError: If the CSV file is not found.
        ValueError: If missing LOCATION_COORDS entries or invalid data.
    """
    global _cached_data
    
    # Return cached data if already loaded
    if _cached_data is not None:
        return _cached_data
    
    file_path = Path("data/doctors_master_sheet.csv")
    
    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path.absolute()}")
    
    try:
        # Load the CSV file
        df = pd.read_csv(file_path)
        
        # 1. Rename columns to standardized names
        column_mapping = {
            'doctors_name': 'name',
            'doctors_location': 'location',
            'doctors_rating': 'rating_score',
            'doctors_number': 'contact_number',
            'doctors_cost': 'consultation_fee',
            'specialty': 'specialty'
        }
        df = df.rename(columns=column_mapping)
        
        # 2. Clean location column: remove trailing commas, strip whitespace, convert to lowercase
        df['location'] = df['location'].str.strip().str.rstrip(',').str.lower()
        
        # 3. Clean rating_score: handle "unavailable", remove '%' symbol, convert to float, divide by 100
        df['rating_score'] = df['rating_score'].replace('unavailable', pd.NA)
        df['rating_score'] = df['rating_score'].astype(str).str.replace('%', '', regex=False)
        df['rating_score'] = pd.to_numeric(df['rating_score'], errors='coerce') / 100
        df['rating_score'] = df['rating_score'].fillna(0.0)
        
        # 4. Clean consultation_fee: remove '₹', convert to integer
        df['consultation_fee'] = df['consultation_fee'].astype(str).str.replace('₹', '', regex=False)
        df['consultation_fee'] = pd.to_numeric(df['consultation_fee'], errors='coerce').astype('Int64')
        
        # 5. Clean contact_number: handle "unavailable", convert to string, remove scientific notation and decimals
        df['contact_number'] = df['contact_number'].replace('unavailable', pd.NA)
        df['contact_number'] = df['contact_number'].astype(str)
        # Remove .0 suffix if present
        df['contact_number'] = df['contact_number'].str.replace(r'\.0$', '', regex=True)
        # Replace 'nan' string with 'unavailable'
        df.loc[df['contact_number'].str.lower() == 'nan', 'contact_number'] = 'unavailable'
        
        # 6. Convert specialty to lowercase
        df['specialty'] = df['specialty'].str.lower()
        
        # 7. Drop rows where name, specialty, or location are missing
        df = df.dropna(subset=['name', 'specialty', 'location'])
        
        # Select only standardized columns (remove profession duplicate)
        df = df[['name', 'specialty', 'location', 'consultation_fee', 'rating_score', 'contact_number']]
        
        # 8. Fill missing consultation fees with 0 (for doctors with unavailable fees)
        df['consultation_fee'] = df['consultation_fee'].fillna(0)
        
        # Ensure data types
        df['consultation_fee'] = df['consultation_fee'].astype('int')
        df['rating_score'] = df['rating_score'].astype('float')
        df['contact_number'] = df['contact_number'].astype('str')
        df['location'] = df['location'].astype('str')
        df['specialty'] = df['specialty'].astype('str')

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


def rank_doctors(df, user_location, severity="medium", top_k=5):
    """
    Rank doctors based on a weighted scoring system adjusted by severity level.
    
    Args:
        df (pd.DataFrame): DataFrame containing doctor data with columns:
            name, specialty, location, consultation_fee, rating_score, contact_number.
        user_location (str): User's preferred location.
        severity (str): Severity level - "low", "medium", "high". Default is "medium".
        top_k (int): Number of top results to return. Default is 5.
    
    Severity-based weighting:
        - "low": Rating 0.5, Cost 0.3, Location 0.2 (standard)
        - "medium": Rating 0.5, Cost 0.3, Location 0.2 (standard)
        - "high": Rating 0.6, Cost 0.2, Location 0.2 (prioritizes quality)
    
    Returns:
        list: List of dictionaries with top_k doctors sorted by final_score.
              Each dict contains: name, specialty, location, 
              consultation_fee, rating_score, final_score, reason, contact_number, latitude, longitude.
    """
    # Validate required columns
    required_columns = {'name', 'specialty', 'location', 'consultation_fee', 'rating_score', 'contact_number'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")
    
    # Create a copy to avoid modifying original data
    df = df.copy()
    
    # Compute scores
    df['cost_score'] = _compute_cost_score(df['consultation_fee'])
    df['location_score'] = _compute_location_score(df['location'], user_location)
    
    # Determine weights based on severity
    if severity == "high":
        rating_weight = 0.6
        cost_weight = 0.2
        location_weight = 0.2
    else:  # "low" and "medium" use same weights
        rating_weight = 0.5
        cost_weight = 0.3
        location_weight = 0.2
    
    # Compute final score with severity-adjusted weights
    df['final_score'] = (
        rating_weight * df['rating_score'] +
        cost_weight * df['cost_score'] +
        location_weight * df['location_score']
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
            'contact_number': _get_valid_contact_number(row['contact_number']),
            'latitude': latitude,
            'longitude': longitude
        })
    
    return results


def recommend_doctors(input_data: dict):
    """
    Recommend doctors based on specialty, location, and severity preferences.
    
    Fallback logic:
    1. Try exact specialty + exact location
    2. Try exact specialty + nearby locations (via NEARBY_MAP)
    3. Try general_physician + exact location
    4. Try general_physician + nearby locations
    
    Args:
        input_data (dict): Dictionary containing:
            - "specialty" (str): Desired medical specialty (required)
            - "location" (str): Preferred location (required)
            - "severity" (str): Severity level - "low", "medium", "high" (optional, default: "medium")
    
    Returns:
        dict: Dictionary with keys:
            - "recommended_doctors": List of recommended doctor dicts
            - "total_matches": Total doctors matching the specialty
            - "metadata": Fallback information
            - "message": Optional message if no matches found
    """
    # Extract parameters
    specialty = input_data.get("specialty", "").strip().lower()
    location = input_data.get("location", "").strip().lower()
    severity = input_data.get("severity", "medium").strip().lower()
    
    # Validate inputs
    if not specialty or not location:
        raise ValueError("Both 'specialty' and 'location' are required.")
    
    # Load dataset
    df = load_doctors_data()
    
    # Normalize specialty: convert singular to plural if needed
    # Handle common singular/plural variations
    if specialty.endswith('ist') and not specialty.endswith('ists'):
        specialty_variants = [specialty, specialty + 's']
    else:
        specialty_variants = [specialty]
    
    # Filter by specialty - try all variants
    filtered_df = df[df['specialty'].isin(specialty_variants)]

    fallback_applied = False
    fallback_location = None
    fallback_type = None
    original_specialty = specialty

    if filtered_df.empty:
        # No exact specialty match - this could be valid if it genuinely doesn't exist
        # Don't auto-fallback here, let the location filtering handle it
        pass
    else:
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
        
        filtered_df = location_filtered
    
    # If still no matches, try general_physician fallback
    if filtered_df.empty:
        gp_df = df[df['specialty'].str.lower() == "general physician"]
        
        # Try exact location first
        gp_location_filtered = gp_df[gp_df['location'].str.lower() == location]
        
        # If no GPs in exact location, try nearby
        if gp_location_filtered.empty:
            nearby_locations = NEARBY_MAP.get(location, [])
            for nearby in nearby_locations:
                nearby_gp = gp_df[gp_df['location'].str.lower() == nearby]
                if not nearby_gp.empty:
                    gp_location_filtered = nearby_gp
                    fallback_applied = True
                    fallback_location = nearby
                    fallback_type = "general_physician_nearby"
                    break
        
        if not gp_location_filtered.empty:
            filtered_df = gp_location_filtered
            fallback_type = "general_physician"
    
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
    
    # Rank doctors based on severity
    recommended = rank_doctors(filtered_df, location, severity=severity, top_k=DEFAULT_TOP_K)
    
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


def _map_specialty_to_hospital_format(specialty: str) -> list:
    """
    Map doctor specialty names to hospital specialty names.
    Handles conversion like 'cardiologist' -> 'cardiology'.
    
    Args:
        specialty (str): Doctor specialty name (lowercase)
    
    Returns:
        list: List of possible hospital specialty names to search for
    """
    # Mapping from doctor specialties to hospital specialties
    specialty_map = {
        'cardiologist': ['cardiology'],
        'dentist': ['dentistry', 'dental'],
        'dentists': ['dentistry', 'dental'],
        'dermatologist': ['dermatology'],
        'endocrinologist': ['endocrinology'],
        'ent specialist': ['ent', 'ear nose throat'],
        'gastroenterologist': ['gastroenterology'],
        'general physician': ['general physician', 'general medicine'],
        'gynac': ['gynecology', 'obstetrics and gynaecology'],
        'internal medicine': ['internal medicine'],
        'nephrologist': ['nephrology'],
        'obsstetrician': ['obstetrics'],
        'oncologist': ['oncology'],
        'ophthalmologist': ['ophthalmology', 'eye'],
        'orthopedic': ['orthopedic', 'orthopedics'],
        'pediatrician': ['pediatrics', 'paediatrics'],
        'psychiatrist': ['psychiatry'],
        'pulmonologist': ['pulmonology', 'respiratory'],
        'urologist': ['urology'],
    }
    
    # Get mapped specialties, or use original if no mapping found
    mapped = specialty_map.get(specialty, [specialty])
    return mapped


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


def hospital_recommendation_engine(location: str, specialty: str = None):
    """
    Recommend hospitals based on location and optional specialty requirement.
    
    Args:
        location (str): Preferred location (required, case-insensitive)
        specialty (str): Optional medical specialty to filter hospitals by capabilities
    
    Returns:
        dict: Dictionary with keys:
            - "recommended_hospitals": List of hospital dicts
            - "total_matches": Total hospitals found
            - "message": Optional message if no hospitals found
    
    Hospital dict contains:
        - hospital_name, location, hospital_type, emergency_available, 
          icu_available, specialties_available, latitude, longitude, contact_number
    """
    try:
        file_path = Path("data/hospitals.csv")
        
        if not file_path.exists():
            return {
                "recommended_hospitals": [],
                "total_matches": 0,
                "message": "Hospital data not available."
            }
        
        # Load hospitals data
        hospitals_df = pd.read_csv(file_path)
        
        # Standardize location to lowercase
        location = location.strip().lower()
        
        # Filter by location (case insensitive)
        location_filtered = hospitals_df[hospitals_df['location'].str.lower() == location]
        
        if location_filtered.empty:
            return {
                "recommended_hospitals": [],
                "total_matches": 0,
                "message": f"No hospitals found in {location}."
            }
        
        # Optional: filter by specialty if provided
        if specialty:
            specialty = specialty.strip().lower()
            # Filter hospitals that have the specialty in their specialties_available
            location_filtered = location_filtered[
                location_filtered['specialties_available'].str.lower().str.contains(specialty, na=False)
            ]
        
        if location_filtered.empty:
            return {
                "recommended_hospitals": [],
                "total_matches": 0,
                "message": f"No hospitals found in {location} with {specialty} specialty."
            }
        
        # Format results
        results = []
        for _, row in location_filtered.iterrows():
            results.append({
                'hospital_name': row['hospital_name'],
                'location': row['location'],
                'hospital_type': row['hospital_type'],
                'emergency_available': bool(row['emergency_available']),
                'icu_available': bool(row['icu_available']),
                'specialties_available': row['specialties_available'],
                'contact_number': _get_valid_contact_number(row['contact_number']),
                'latitude': float(_convert_to_json_serializable(row['latitude'])),
                'longitude': float(_convert_to_json_serializable(row['longitude']))
            })
        
        return {
            "recommended_hospitals": results,
            "total_matches": len(results)
        }
    
    except Exception as e:
        return {
            "recommended_hospitals": [],
            "total_matches": 0,
            "message": f"Error retrieving hospital data: {str(e)}"
        }


def recommend_hospitals(input_data: dict):
    """
    Recommend hospitals based on location, specialty, and emergency requirements.
    
    Filtering logic:
    1. Load hospital dataset
    2. Filter by location (exact match first, then NEARBY_MAP fallback)
    3. Filter by emergency_available == True for high severity
    4. Filter by specialty (must be in specialties_available list)
    5. Rank hospitals by location proximity (exact match first) and hospital_type preference
    6. Return top DEFAULT_TOP_K hospitals
    
    Args:
        input_data (dict): Dictionary containing:
            - "location" (str): Preferred location (required)
            - "specialty" (str): Medical specialty (required)
            - "severity" (str): Severity level - "low", "medium", "high" (optional, default: "medium")
    
    Returns:
        dict: Dictionary with keys:
            - "care_setting": "hospital"
            - "recommended_hospitals": List of hospital dicts sorted by score
            - "total_matches": Total hospitals found
            - "metadata": Fallback and filtering information
            - "message": Optional message if no hospitals found
    
    Hospital dict contains:
        - hospital_name, location, hospital_type, emergency_available, 
          icu_available, specialties_available, latitude, longitude, contact_number, score
    """
    try:
        # Extract parameters
        location = input_data.get("location", "").strip().lower()
        specialty = input_data.get("specialty", "").strip().lower()
        severity = input_data.get("severity", "medium").strip().lower()
        
        # Validate inputs
        if not location or not specialty:
            raise ValueError("Both 'location' and 'specialty' are required.")
        
        file_path = Path("data/hospitals.csv")
        
        if not file_path.exists():
            return {
                "care_setting": "hospital",
                "recommended_hospitals": [],
                "total_matches": 0,
                "message": "Hospital data not available.",
                "metadata": {
                    "fallback_applied": False,
                    "fallback_location": None
                }
            }
        
        # Load hospitals data
        hospitals_df = pd.read_csv(file_path)
        
        # Convert location to lowercase for comparison
        hospitals_df['location_lower'] = hospitals_df['location'].str.lower()
        
        fallback_applied = False
        fallback_location = None
        
        # Step 1: Filter by location (exact match first, then nearby)
        location_filtered = hospitals_df[hospitals_df['location_lower'] == location]
        fallback_applied = False
        fallback_location = None
        
        # If no exact results, try nearby locations
        if location_filtered.empty:
            nearby_locations = NEARBY_MAP.get(location, [])
            for nearby in nearby_locations:
                nearby_filtered = hospitals_df[hospitals_df['location_lower'] == nearby]
                
                # If high severity, check if this nearby location has emergency hospitals
                if severity == "high":
                    nearby_emergency = nearby_filtered[nearby_filtered['emergency_available'].astype(bool)]
                    if not nearby_emergency.empty:
                        location_filtered = nearby_emergency
                        fallback_applied = True
                        fallback_location = nearby
                        break
                else:
                    # For non-high severity, accept any hospitals
                    if not nearby_filtered.empty:
                        location_filtered = nearby_filtered
                        fallback_applied = True
                        fallback_location = nearby
                        break
        
        if location_filtered.empty:
            # Try one more time: for high severity, check if there are ANY emergency hospitals
            # in nearby locations (not just the specialty filter)
            if severity == "high":
                return {
                    "care_setting": "hospital",
                    "recommended_hospitals": [],
                    "total_matches": 0,
                    "message": "No emergency-capable hospitals found in this area or nearby locations.",
                    "metadata": {
                        "fallback_applied": False,
                        "fallback_location": None
                    }
                }
            else:
                return {
                    "care_setting": "hospital",
                    "recommended_hospitals": [],
                    "total_matches": 0,
                    "message": f"No hospitals found in {location} or nearby locations.",
                    "metadata": {
                        "fallback_applied": False,
                        "fallback_location": None
                    }
                }
        
        # Step 2: Filter by emergency_available if high severity (for exact location match)
        # For nearby locations, we've already applied this filter above
        if severity == "high" and not fallback_applied:
            location_filtered = location_filtered[location_filtered['emergency_available'].astype(bool)]
            
            if location_filtered.empty:
                # No emergency hospitals in exact location, try nearby
                nearby_locations = NEARBY_MAP.get(location, [])
                for nearby in nearby_locations:
                    nearby_filtered = hospitals_df[hospitals_df['location_lower'] == nearby]
                    nearby_emergency = nearby_filtered[nearby_filtered['emergency_available'].astype(bool)]
                    if not nearby_emergency.empty:
                        location_filtered = nearby_emergency
                        fallback_applied = True
                        fallback_location = nearby
                        break
                
                if location_filtered.empty:
                    return {
                        "care_setting": "hospital",
                        "recommended_hospitals": [],
                        "total_matches": 0,
                        "message": "No emergency-capable hospitals found in this area or nearby locations.",
                        "metadata": {
                            "fallback_applied": False,
                            "fallback_location": None
                        }
                    }
        
        # Step 3: Filter by specialty (must be in specialties_available)
        # Map doctor specialty names to hospital specialty names (e.g., 'cardiologist' -> 'cardiology')
        hospital_specialties = _map_specialty_to_hospital_format(specialty)
        specialty_pattern = '|'.join(hospital_specialties)
        specialty_filtered = location_filtered[
            location_filtered['specialties_available'].str.lower().str.contains(specialty_pattern, na=False, regex=True)
        ]
        
        # If no hospitals with specialty found, allow any emergency hospitals for high severity
        # (for emergency cases, having an emergency-capable hospital is more important than specialty match)
        if specialty_filtered.empty and severity == "high":
            location_filtered = location_filtered  # Use location_filtered (which already has emergency hospitals)
        elif specialty_filtered.empty and fallback_applied and severity == "high":
            # No specialty match even in fallback location, use all emergency hospitals from fallback
            location_filtered = hospitals_df[hospitals_df['location_lower'] == fallback_location]
            location_filtered = location_filtered[location_filtered['emergency_available'].astype(bool)]
        else:
            location_filtered = specialty_filtered
        
        if location_filtered.empty:
            return {
                "care_setting": "hospital",
                "recommended_hospitals": [],
                "total_matches": 0,
                "message": f"No hospitals found with {specialty} specialty.",
                "metadata": {
                    "fallback_applied": fallback_applied,
                    "fallback_location": fallback_location
                }
            }
        
        # Get total matches before ranking
        total_matches = len(location_filtered)
        
        # Step 4: Rank hospitals by location proximity and hospital_type preference
        location_filtered = location_filtered.copy()
        
        # Score for location proximity (exact match = 1.0, nearby = 0.7)
        location_filtered['location_score'] = location_filtered['location_lower'].apply(
            lambda x: 1.0 if x == location else 0.7
        )
        
        # Score for hospital type (private = 1.0, public = 0.8, others = 0.6)
        def get_hospital_type_score(h_type):
            h_type_lower = str(h_type).lower() if h_type else ""
            if "private" in h_type_lower:
                return 1.0
            elif "public" in h_type_lower or "government" in h_type_lower:
                return 0.8
            else:
                return 0.6
        
        location_filtered['hospital_type_score'] = location_filtered['hospital_type'].apply(
            get_hospital_type_score
        )
        
        # Score for emergency services (true = 0.3 boost, false = 0)
        location_filtered['emergency_score'] = location_filtered['emergency_available'].astype(bool).apply(
            lambda x: 0.3 if x else 0.0
        )
        
        # Score for ICU availability (true = 0.2 boost, false = 0)
        location_filtered['icu_score'] = location_filtered['icu_available'].astype(bool).apply(
            lambda x: 0.2 if x else 0.0
        )
        
        # Compute final score: location (0.5) + hospital_type (0.3) + emergency (0.1) + icu (0.1)
        location_filtered['score'] = (
            0.5 * location_filtered['location_score'] +
            0.3 * location_filtered['hospital_type_score'] +
            0.1 * location_filtered['emergency_score'] +
            0.1 * location_filtered['icu_score']
        )
        
        # Step 5: Get top DEFAULT_TOP_K hospitals sorted by score descending
        top_hospitals = location_filtered.nlargest(DEFAULT_TOP_K, 'score')
        
        # Step 6: Format results
        results = []
        for _, row in top_hospitals.iterrows():
            results.append({
                'hospital_name': row['hospital_name'],
                'location': row['location'],
                'hospital_type': row['hospital_type'],
                'emergency_available': bool(row['emergency_available']),
                'icu_available': bool(row['icu_available']),
                'specialties_available': row['specialties_available'],
                'contact_number': _get_valid_contact_number(row['contact_number']),
                'latitude': float(_convert_to_json_serializable(row['latitude'])),
                'longitude': float(_convert_to_json_serializable(row['longitude'])),
                'score': round(float(_convert_to_json_serializable(row['score'])), 4)
            })
        
        # Return structured response
        return {
            "care_setting": "hospital",
            "recommended_hospitals": results,
            "total_matches": total_matches,
            "metadata": {
                "fallback_applied": fallback_applied,
                "fallback_location": fallback_location,
                "emergency_filter_applied": severity == "high",
                "specialty_requested": specialty
            }
        }
    
    except Exception as e:
        return {
            "care_setting": "hospital",
            "recommended_hospitals": [],
            "total_matches": 0,
            "message": f"Error processing hospital recommendations: {str(e)}",
            "metadata": {
                "fallback_applied": False,
                "fallback_location": None
            }
        }


def generate_recommendation_response(input_data: dict):
    """
    Generate a comprehensive recommendation response with severity-based routing.
    
    Routes requests based on severity level:
    - "high": Hospital-only with strict emergency filtering (no fallback)
    - "medium": Hospitals first, fallback to doctors if no hospitals available
    - "low": Doctor recommendations only for routine checkups
    
    Args:
        input_data (dict): Dictionary containing:
            - "specialty" (str): Desired medical specialty (required)
            - "location" (str OR dict): Location as string name OR dict with "latitude" and "longitude" (required)
            - "severity" (str): Severity level - "low", "medium", or "high" (optional, default: "medium")
    
    Returns:
        dict: Dictionary with either recommended_doctors or recommended_hospitals
              based on severity-based routing logic, or error dict
    """
    # INPUT VALIDATION
    if not isinstance(input_data, dict):
        return {"error": "Invalid input format."}
    
    specialty = input_data.get("specialty", "").strip().lower()
    if not specialty:
        return {"error": "Specialty is required."}
    
    # LOCATION HANDLING - Support both string and lat/lng coordinates
    location_input = input_data.get("location")
    if not location_input:
        return {"error": "Location is required."}
    
    # Check if location is provided as coordinates
    if isinstance(location_input, dict):
        latitude = location_input.get("latitude")
        longitude = location_input.get("longitude")
        
        if latitude is None or longitude is None:
            return {"error": "Location coordinates must include both latitude and longitude."}
        
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (ValueError, TypeError):
            return {"error": "Invalid latitude or longitude values."}
        
        # Convert coordinates to nearest location name
        detected_location = convert_coordinates_to_location(latitude, longitude)
        if detected_location is None:
            return {
                "error": "No known locations found near the provided coordinates. Please try a different location.",
                "metadata": {
                    "provided_coordinates": {"latitude": latitude, "longitude": longitude}
                }
            }
        location = detected_location
        location_source = "coordinates"
    else:
        # Location provided as string
        location = str(location_input).strip().lower()
        if not location:
            return {"error": "Location is required."}
        location_source = "name"
    
    # SEVERITY VALIDATION
    severity = input_data.get("severity", "medium").strip().lower()
    if severity not in ["low", "medium", "high"]:
        return {"error": "Invalid severity. Must be low, medium, or high."}
    
    # Prepare cleaned input for downstream functions
    cleaned_input = {
        "specialty": specialty,
        "location": location,
        "severity": severity
    }
    
    # SEVERITY-BASED ROUTING
    if severity == "high":
        # HIGH: Strict emergency filtering via hospital engine
        hospital_results = recommend_hospitals(cleaned_input)
        hospital_count = hospital_results.get("total_matches", 0)
        
        # Strict requirement: no fallback if no emergency hospitals found
        if hospital_count == 0:
            return {"error": "No emergency-capable hospital found in this area."}
        
        return {
            "care_setting": "hospital",
            "metadata": {
                "query_specialty": specialty,
                "query_location": location,
                "query_severity": severity,
                "severity": severity,
                "recommendation_type": "hospital_only",
                "emergency_filter_applied": True,
                "location_source": location_source,
                "detected_location": location if location_source == "coordinates" else None
            },
            "recommended_hospitals": hospital_results.get("recommended_hospitals", []),
            "total_hospitals_available": hospital_count
        }
    
    elif severity == "medium":
        # MEDIUM: Try hospitals first, fallback to doctors if empty
        hospital_results = recommend_hospitals(cleaned_input)
        hospital_count = hospital_results.get("total_matches", 0)
        
        if hospital_count > 0:
            # Hospitals found - return hospital recommendations
            return {
                "care_setting": "hospital",
                "metadata": {
                    "query_specialty": specialty,
                    "query_location": location,
                    "query_severity": severity,
                    "severity": severity,
                    "recommendation_type": "hospital_primary",
                    "location_source": location_source,
                    "detected_location": location if location_source == "coordinates" else None
                },
                "recommended_hospitals": hospital_results.get("recommended_hospitals", []),
                "total_hospitals_available": hospital_count
            }
        else:
            # No hospitals found - fallback to doctors
            doctor_recommendations = recommend_doctors(cleaned_input)
            cost_insights = generate_cost_insights(cleaned_input)
            
            returned_count = len(doctor_recommendations.get("recommended_doctors", []))
            total_matches = doctor_recommendations.get("total_matches", 0)
            fallback_metadata = doctor_recommendations.get("metadata", {})
            fallback_type = fallback_metadata.get("fallback_type")
            
            metadata = {
                "query_specialty": specialty,
                "query_location": location,
                "query_severity": severity,
                "severity": severity,
                "recommendation_type": "doctor_fallback",
                "total_doctors_available": total_matches,
                "returned_count": returned_count,
                "fallback_applied": fallback_metadata.get("fallback_applied", False),
                "fallback_location": fallback_metadata.get("fallback_location"),
                "fallback_type": fallback_type,
                "location_source": location_source,
                "detected_location": location if location_source == "coordinates" else None
            }
            
            if fallback_type == "general_physician":
                metadata["original_specialty"] = fallback_metadata.get("original_specialty", specialty)
            
            response = {
                "care_setting": "clinic",
                "metadata": metadata,
                "recommended_doctors": doctor_recommendations.get("recommended_doctors", []),
                "cost_summary": {
                    "average_fee": cost_insights.get("average_fee"),
                    "min_fee": cost_insights.get("min_fee"),
                    "max_fee": cost_insights.get("max_fee"),
                    "cost_band": cost_insights.get("cost_band")
                }
            }
            
            if "message" in doctor_recommendations:
                response["message"] = doctor_recommendations["message"]
            
            return response
    
    else:  # severity == "low"
        # LOW: Doctor engine only, with hospital fallback if no doctors found
        doctor_recommendations = recommend_doctors(cleaned_input)
        doctor_count = len(doctor_recommendations.get("recommended_doctors", []))
        
        # If no doctors found, fallback to hospitals
        if doctor_count == 0:
            hospital_results = recommend_hospitals(cleaned_input)
            hospital_count = hospital_results.get("total_matches", 0)
            
            if hospital_count > 0:
                # Return hospital recommendations as fallback
                return {
                    "care_setting": "hospital",
                    "metadata": {
                        "query_specialty": specialty,
                        "query_location": location,
                        "query_severity": severity,
                        "severity": severity,
                        "recommendation_type": "hospital_fallback",
                        "reason": "No doctors available, suggesting hospitals instead",
                        "location_source": location_source,
                        "detected_location": location if location_source == "coordinates" else None
                    },
                    "recommended_hospitals": hospital_results.get("recommended_hospitals", []),
                    "total_hospitals_available": hospital_count
                }
        
        # Otherwise, continue with doctor recommendations
        cost_insights = generate_cost_insights(cleaned_input)
        
        returned_count = len(doctor_recommendations.get("recommended_doctors", []))
        total_matches = doctor_recommendations.get("total_matches", 0)
        fallback_metadata = doctor_recommendations.get("metadata", {})
        fallback_type = fallback_metadata.get("fallback_type")
        
        metadata = {
            "query_specialty": specialty,
            "query_location": location,
            "query_severity": severity,
            "severity": severity,
            "recommendation_type": "doctor_only",
            "total_doctors_available": total_matches,
            "returned_count": returned_count,
            "fallback_applied": fallback_metadata.get("fallback_applied", False),
            "fallback_location": fallback_metadata.get("fallback_location"),
            "fallback_type": fallback_type,
            "location_source": location_source,
            "detected_location": location if location_source == "coordinates" else None
        }
        
        if fallback_type == "general_physician" or fallback_type == "general_physician_nearby":
            metadata["original_specialty"] = fallback_metadata.get("original_specialty", specialty)
        
        response = {
            "care_setting": "clinic",
            "metadata": metadata,
            "recommended_doctors": doctor_recommendations.get("recommended_doctors", []),
            "cost_summary": {
                "average_fee": cost_insights.get("average_fee"),
                "min_fee": cost_insights.get("min_fee"),
                "max_fee": cost_insights.get("max_fee"),
                "cost_band": cost_insights.get("cost_band")
            }
        }
        
        if "message" in doctor_recommendations:
            response["message"] = doctor_recommendations["message"]
        
        return response
