#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Function to run a test and print the result
run_test() {
    echo -e "${GREEN}Running: $1${NC}"
    curl -s -X POST http://127.0.0.1:5001$2 \
        -H "Content-Type: application/json" \
        -d "$3" | jq '.'
    echo -e "\n"
}

# Base user profile and event context
USER_PROFILE='{
    "height": 165,
    "weight": 60,
    "bust": 85,
    "waist": 70,
    "hips": 90,
    "inseam": 75,
    "shoe_size": 38,
    "comfort_level": 4,
    "style_preferences": ["casual", "elegant"],
    "color_preferences": ["blue", "black"],
    "fit_preferences": ["regular", "slim"]
}'

# Test complete outfit generation for different seasons
print_section "Testing Complete Outfit Generation"

# Summer outfit
SUMMER_CONTEXT='{
    "event_type": "casual_gathering",
    "formality_level": 3,
    "weather_conditions": ["sunny", "hot", "humid"],
    "time_of_day": "afternoon",
    "season": "summer",
    "location": "outdoor",
    "duration": 120,
    "activity_level": 2
}'
run_test "Summer Outfit" "/api/generate/complete-outfit" "{\"user_profile\": $USER_PROFILE, \"event_context\": $SUMMER_CONTEXT}"

# Winter outfit
WINTER_CONTEXT='{
    "event_type": "casual_gathering",
    "formality_level": 3,
    "weather_conditions": ["cold", "snowy", "windy"],
    "time_of_day": "afternoon",
    "season": "winter",
    "location": "outdoor",
    "duration": 120,
    "activity_level": 2
}'
run_test "Winter Outfit" "/api/generate/complete-outfit" "{\"user_profile\": $USER_PROFILE, \"event_context\": $WINTER_CONTEXT}"

# Spring outfit
SPRING_CONTEXT='{
    "event_type": "casual_gathering",
    "formality_level": 3,
    "weather_conditions": ["mild", "rainy", "breezy"],
    "time_of_day": "afternoon",
    "season": "spring",
    "location": "outdoor",
    "duration": 120,
    "activity_level": 2
}'
run_test "Spring Outfit" "/api/generate/complete-outfit" "{\"user_profile\": $USER_PROFILE, \"event_context\": $SPRING_CONTEXT}"

# Fall outfit
FALL_CONTEXT='{
    "event_type": "casual_gathering",
    "formality_level": 3,
    "weather_conditions": ["cool", "windy", "rainy"],
    "time_of_day": "afternoon",
    "season": "fall",
    "location": "outdoor",
    "duration": 120,
    "activity_level": 2
}'
run_test "Fall Outfit" "/api/generate/complete-outfit" "{\"user_profile\": $USER_PROFILE, \"event_context\": $FALL_CONTEXT}"

# Test individual item generation
print_section "Testing Individual Item Generation"

# Summer top
run_test "Summer Top" "/api/generate/top" "{\"user_profile\": $USER_PROFILE, \"event_context\": $SUMMER_CONTEXT}"

# Winter bottom
run_test "Winter Bottom" "/api/generate/bottom" "{\"user_profile\": $USER_PROFILE, \"event_context\": $WINTER_CONTEXT}"

# Spring shoes
run_test "Spring Shoes" "/api/generate/shoes" "{\"user_profile\": $USER_PROFILE, \"event_context\": $SPRING_CONTEXT}"

# Test measurement endpoints
print_section "Testing Measurement Endpoints"

# Validate measurements
run_test "Validate Measurements" "/api/measurements/validate" "$USER_PROFILE"

# Get measurement guide
echo -e "${GREEN}Getting Measurement Guide${NC}"
curl -s -X GET http://127.0.0.1:5001/api/measurements/guide | jq '.'
echo -e "\n"

# Determine body type
BODY_TYPE_PROFILE='{
    "height": 165,
    "weight": 60,
    "bust": 85,
    "waist": 70,
    "hips": 90,
    "shoulder_width": 38
}'
run_test "Determine Body Type" "/api/measurements/body-type" "$BODY_TYPE_PROFILE"

# Test special requirements
print_section "Testing Special Requirements"

# Pregnant user profile
PREGNANT_PROFILE='{
    "height": 165,
    "weight": 60,
    "bust": 85,
    "waist": 70,
    "hips": 90,
    "inseam": 75,
    "shoe_size": 38,
    "comfort_level": 4,
    "style_preferences": ["casual", "elegant"],
    "color_preferences": ["blue", "black"],
    "fit_preferences": ["regular", "slim"],
    "special_requirement": "pregnant"
}'
run_test "Pregnant User Outfit" "/api/generate/complete-outfit" "{\"user_profile\": $PREGNANT_PROFILE, \"event_context\": $SUMMER_CONTEXT}"

# Test different formality levels
print_section "Testing Different Formality Levels"

# Formal event
FORMAL_CONTEXT='{
    "event_type": "wedding",
    "formality_level": 8,
    "weather_conditions": ["sunny", "warm"],
    "time_of_day": "afternoon",
    "season": "summer",
    "location": "outdoor",
    "duration": 120,
    "activity_level": 1
}'
run_test "Formal Event Outfit" "/api/generate/complete-outfit" "{\"user_profile\": $USER_PROFILE, \"event_context\": $FORMAL_CONTEXT}"

# Business event
BUSINESS_CONTEXT='{
    "event_type": "business_meeting",
    "formality_level": 5,
    "weather_conditions": ["mild", "clear"],
    "time_of_day": "morning",
    "season": "spring",
    "location": "indoor",
    "duration": 60,
    "activity_level": 1
}'
run_test "Business Event Outfit" "/api/generate/complete-outfit" "{\"user_profile\": $USER_PROFILE, \"event_context\": $BUSINESS_CONTEXT}"

echo -e "${GREEN}All tests completed!${NC}" 