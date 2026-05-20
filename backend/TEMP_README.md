# Doctor Recommendation Engine

A FastAPI-based service that recommends doctors based on specialty, location, and ranking metrics.

## Features

- **Smart Doctor Ranking**: Weighted scoring system (rating 50%, cost 30%, location 20%)
- **Location Fallback**: Attempts nearby locations if exact match not found
- **Specialty Fallback**: Falls back to general physicians if specialty unavailable
- **Cost Insights**: Provides average, min, max fees and cost band classification
- **Geo-coordinates**: Returns latitude/longitude for each doctor
- **JSON API**: FastAPI-powered REST endpoints

## Project Structure

```
scraper/
├── data_loader.py              # Core logic (data loading, ranking, recommendations)
├── data/
│   └── doctors.csv             # Doctor dataset (579 records)
├── backend/
│   ├── api/
│   │   └── recommendation_api.py   # FastAPI router
│   └── tests/
│       └── test_engine.py      # Test script
└── TEMP_README.md
```

## Installation

```bash
pip install pandas fastapi uvicorn
```

## Usage

### As Python Module

```python
from data_loader import generate_recommendation_response

response = generate_recommendation_response({
    "specialty": "Dentist",
    "location": "Baner"
})

import json
print(json.dumps(response, indent=2))
```

### As API

```bash
# Start server (requires main app file with router integration)
uvicorn main:app --reload

# POST /recommend
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"specialty": "Dentist", "location": "Baner"}'
```

## Input Format

```json
{
  "specialty": "string (required)",
  "location": "string (required)"
}
```

Example:
```json
{
  "specialty": "Dentist",
  "location": "Baner"
}
```

## Output Format

```json
{
  "metadata": {
    "query_specialty": "dentist",
    "query_location": "baner",
    "total_doctors_available": 277,
    "returned_count": 10,
    "ranking_weights": {
      "rating_weight": 0.5,
      "cost_weight": 0.3,
      "location_weight": 0.2
    },
    "fallback_applied": false,
    "fallback_location": null,
    "fallback_type": null,
    "original_specialty": null
  },
  "recommended_doctors": [
    {
      "name": "Dr. Dragpal Singh Rajput",
      "specialty": "Dentist",
      "location": "baner",
      "consultation_fee": 100,
      "rating_score": 0.94,
      "final_score": 0.97,
      "reason": "Highly rated • Affordable • Nearby",
      "latitude": 18.5590,
      "longitude": 73.7890
    }
  ],
  "total_matches": 277,
  "cost_summary": {
    "average_fee": 471.43,
    "min_fee": 100.0,
    "max_fee": 1000.0,
    "cost_band": "Standard"
  }
}
```

## Ranking Logic

**Final Score** = 0.5 × rating_score + 0.3 × cost_score + 0.2 × location_score

- **Rating Score**: Doctor's rating (0–1)
- **Cost Score**: Normalized inverse of consultation fee (lower fee = higher score)
- **Location Score**: 1.0 if exact match, 0.5 otherwise

## Reason Tags

Each doctor includes a `reason` field with applicable tags:

- **Highly rated**: rating_score ≥ 0.9
- **Affordable**: consultation_fee in bottom 25%
- **Nearby**: location exactly matches user location
- **Balanced recommendation**: no tags apply

Tags are combined with " • " separator.

## Fallback Strategy

1. **Exact Match**: Search specialty + exact location
2. **Nearby Locations**: Use NEARBY_MAP for ordered fallback locations
3. **General Physician**: Fall back to GP specialty in original location
4. **No Results**: Return empty list with clear message

Fallback details are included in metadata:
- `fallback_applied`: boolean
- `fallback_location`: nearby location used (or null)
- `fallback_type`: "nearby" or "general_physician" (or null)
- `original_specialty`: originally requested specialty

## Cost Bands

- **Budget-friendly**: average_fee < 300
- **Standard**: 300 ≤ average_fee ≤ 500
- **Premium**: average_fee > 500

## Testing

```bash
cd /Users/sumedhjaltare/Desktop/scraper
python3 backend/tests/test_engine.py
```

## Key Constants

- `DEFAULT_TOP_K`: 10 (max doctors returned per request)
- `NEARBY_MAP`: Predefined proximity map for all 81 Pune locations
- `LOCATION_COORDS`: Latitude/longitude for all locations
- `LOCATION_COORDS` validation ensures coordinates are valid (lat: -90 to 90, lon: -180 to 180)

## Error Handling

Invalid requests return structured error responses:

```json
{
  "error": "Specialty is required."
}
```

Possible errors:
- `"Invalid input format."` - input is not a dict
- `"Specialty is required."` - missing specialty
- `"Location is required."` - missing location
- `"Internal server error."` - unexpected exception in API

## Data Validation

- All locations in dataset are present in LOCATION_COORDS
- All coordinates are within valid geographic ranges
- LOCATION_COORDS keys are lowercase
- Dataset has 579 doctor records with 81 unique locations

## Notes

- Input specialty and location are case-insensitive and automatically lowercased
- Whitespace is automatically stripped from inputs
- Responses are fully JSON-serializable (no numpy types)
- All numeric outputs use native Python types (int, float)
- Consultation fees are integers; ratings/scores are floats (2-4 decimals)

---

**Status**: Temporary documentation  
**Last Updated**: February 20, 2026
