#!/bin/bash
# API Testing Script for Healthcare Platform
# Run this in Git Bash while the server is running

echo "======================================================================"
echo "Healthcare Platform API Tests"
echo "======================================================================"
echo ""

BASE_URL="http://localhost:8000"

echo "1. Testing Health Check..."
curl -s "$BASE_URL/health" | python -m json.tool
echo ""
echo ""

echo "======================================================================"
echo "2. Testing with LOCATION - Headache and Fever"
echo "======================================================================"
curl -s -X POST "$BASE_URL/api/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have severe headache and fever for 2 days",
    "session_id": "test_location_1",
    "location": {
      "city": "Mumbai",
      "state": "Maharashtra",
      "country": "India",
      "latitude": 19.0760,
      "longitude": 72.8777
    }
  }' | python -m json.tool

echo ""
echo ""

echo "======================================================================"
echo "3. Testing DERMATOLOGY with Location - Cherry Angioma"
echo "======================================================================"
curl -s -X POST "$BASE_URL/api/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have a cherry angioma on my arm",
    "session_id": "test_derma_1",
    "location": {
      "city": "Delhi",
      "state": "Delhi",
      "country": "India"
    }
  }' | python -m json.tool

echo ""
echo ""

echo "======================================================================"
echo "4. Testing EMERGENCY with Location - Chest Pain"
echo "======================================================================"
curl -s -X POST "$BASE_URL/api/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "severe chest pain and cant breathe",
    "session_id": "test_emergency_1",
    "location": {
      "city": "Bangalore",
      "state": "Karnataka",
      "latitude": 12.9716,
      "longitude": 77.5946
    }
  }' | python -m json.tool

echo ""
echo ""

echo "======================================================================"
echo "5. Testing without Location - Face Pimple"
echo "======================================================================"
curl -s -X POST "$BASE_URL/api/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "face pimple that wont go away",
    "session_id": "test_no_location"
  }' | python -m json.tool

echo ""
echo ""

echo "======================================================================"
echo "6. Testing IRRELEVANT - Greeting"
echo "======================================================================"
curl -s -X POST "$BASE_URL/api/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "hi there"
  }' | python -m json.tool

echo ""
echo ""

echo "======================================================================"
echo "7. Testing INSUFFICIENT_INFO - Vague Symptom"
echo "======================================================================"
curl -s -X POST "$BASE_URL/api/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "pain",
    "location": {
      "city": "Chennai",
      "state": "Tamil Nadu"
    }
  }' | python -m json.tool

echo ""
echo ""
echo "======================================================================"
echo "All Tests Complete!"
echo "======================================================================"
