import pytest
from fastapi.testclient import TestClient
from api import app, UserProfile, EventContext, OutfitRequest
from measurement_utils import BodyType, SpecialRequirement

client = TestClient(app)

# Test data
VALID_USER_PROFILE = {
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
}

VALID_EVENT_CONTEXT = {
    "event_type": "casual_gathering",
    "formality_level": 3,
    "weather_conditions": ["sunny", "warm"],
    "time_of_day": "afternoon",
    "season": "summer",
    "location": "outdoor",
    "duration": 120,
    "activity_level": 2
}

def test_validate_measurements():
    """Test measurement validation endpoint."""
    response = client.post("/api/measurements/validate", json=VALID_USER_PROFILE)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == True

def test_validate_measurements_invalid():
    """Test measurement validation with invalid data."""
    invalid_profile = VALID_USER_PROFILE.copy()
    invalid_profile["height"] = 50  # Too short
    response = client.post("/api/measurements/validate", json=invalid_profile)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == False
    assert len(data["errors"]) > 0

def test_estimate_measurements():
    """Test measurement estimation endpoint."""
    partial_profile = {
        "height": 165,
        "weight": 60,
        "bust": 85
    }
    response = client.post("/api/measurements/estimate", json=partial_profile)
    assert response.status_code == 200
    data = response.json()
    assert "measurements" in data
    assert "body_type" in data
    assert all(key in data["measurements"] for key in ["waist", "hips", "inseam"])

def test_get_measurement_guide():
    """Test measurement guide endpoint."""
    response = client.get("/api/measurements/guide")
    assert response.status_code == 200
    data = response.json()
    assert "guide" in data
    assert "default_measurements" in data
    assert "valid_ranges" in data

def test_determine_body_type():
    """Test body type determination endpoint."""
    response = client.post("/api/measurements/body-type", json=VALID_USER_PROFILE)
    assert response.status_code == 200
    data = response.json()
    assert "body_type" in data
    assert "characteristics" in data
    assert "measurements" in data

def test_generate_top():
    """Test top generation endpoint."""
    request = {
        "user_profile": VALID_USER_PROFILE,
        "event_context": VALID_EVENT_CONTEXT
    }
    response = client.post("/api/generate/top", json=request)
    assert response.status_code == 200
    data = response.json()
    assert "top" in data
    assert all(key in data["top"] for key in ["type", "color", "material", "fit", "style"])

def test_generate_bottom():
    """Test bottom generation endpoint."""
    request = {
        "user_profile": VALID_USER_PROFILE,
        "event_context": VALID_EVENT_CONTEXT
    }
    response = client.post("/api/generate/bottom", json=request)
    assert response.status_code == 200
    data = response.json()
    assert "bottom" in data
    assert all(key in data["bottom"] for key in ["type", "color", "material", "fit", "style"])

def test_generate_shoes():
    """Test shoes generation endpoint."""
    request = {
        "user_profile": VALID_USER_PROFILE,
        "event_context": VALID_EVENT_CONTEXT
    }
    response = client.post("/api/generate/shoes", json=request)
    assert response.status_code == 200
    data = response.json()
    assert "shoes" in data
    assert all(key in data["shoes"] for key in ["type", "heel_height", "closure", "toe", "style", "material"])

def test_generate_complete_outfit():
    """Test complete outfit generation endpoint."""
    request = {
        "user_profile": VALID_USER_PROFILE,
        "event_context": VALID_EVENT_CONTEXT
    }
    response = client.post("/api/generate/complete-outfit", json=request)
    assert response.status_code == 200
    data = response.json()
    assert "outfit" in data
    outfit = data["outfit"]
    assert all(key in outfit for key in [
        "style_preferences", "color_preferences", "materials",
        "suitability", "occasion", "season", "formality_level",
        "comfort_level", "top", "bottom", "shoes"
    ])

def test_special_requirements():
    """Test outfit generation with special requirements."""
    special_profile = VALID_USER_PROFILE.copy()
    special_profile["special_requirement"] = SpecialRequirement.PREGNANT.value
    request = {
        "user_profile": special_profile,
        "event_context": VALID_EVENT_CONTEXT
    }
    response = client.post("/api/generate/complete-outfit", json=request)
    assert response.status_code == 200
    data = response.json()
    outfit = data["outfit"]
    # Verify that shoes have appropriate heel height for pregnant user
    assert outfit["shoes"]["heel_height"] in ["flat", "low"]

def test_seasonal_materials():
    """Test material selection for different seasons."""
    seasons = ["summer", "winter", "spring", "fall"]
    seasonal_materials = {
        "summer": {
            "tops": ["cotton", "linen", "silk", "light", "bamboo", "modal", "synthetic"],
            "bottoms": ["cotton", "linen", "light", "bamboo", "modal", "synthetic"],
            "shoes": ["leather", "canvas", "mesh", "synthetic"]
        },
        "winter": {
            "tops": ["wool", "cashmere", "fleece", "velvet", "cotton", "silk", "synthetic"],
            "bottoms": ["wool", "cashmere", "fleece", "velvet", "cotton", "synthetic"],
            "shoes": ["leather", "suede", "synthetic"]
        },
        "spring": {
            "tops": ["cotton", "linen", "silk", "light", "synthetic", "bamboo", "modal"],
            "bottoms": ["cotton", "linen", "light", "synthetic", "bamboo", "modal"],
            "shoes": ["leather", "canvas", "mesh", "synthetic"]
        },
        "fall": {
            "tops": ["wool", "cotton", "silk", "synthetic", "linen", "light", "bamboo", "modal"],
            "bottoms": ["wool", "cotton", "silk", "synthetic", "linen", "light", "bamboo", "modal"],
            "shoes": ["leather", "suede", "synthetic"]
        }
    }
    
    for season in seasons:
        event_context = VALID_EVENT_CONTEXT.copy()
        event_context["season"] = season
        request = {
            "user_profile": VALID_USER_PROFILE,
            "event_context": event_context
        }
        response = client.post("/api/generate/complete-outfit", json=request)
        assert response.status_code == 200
        data = response.json()
        outfit = data["outfit"]
        
        # Verify that materials list is not empty
        assert outfit["materials"]
        
        # Verify that the selected materials are appropriate for the season
        top_material = outfit["top"]["material"]
        bottom_material = outfit["bottom"]["material"]
        shoes_material = outfit["shoes"]["material"]
        
        # Check if the materials are in the available materials list
        assert top_material in outfit["materials"]
        assert bottom_material in outfit["materials"]
        
        # Check if the materials are appropriate for the season
        assert top_material in seasonal_materials[season]["tops"], f"Invalid top material {top_material} for {season}"
        assert bottom_material in seasonal_materials[season]["bottoms"], f"Invalid bottom material {bottom_material} for {season}"
        assert shoes_material in seasonal_materials[season]["shoes"], f"Invalid shoes material {shoes_material} for {season}"

def test_style_context():
    """Test outfit generation for different style contexts."""
    style_contexts = [
        ("wedding", "formal"),
        ("business_meeting", "business"),
        ("casual_gathering", "casual")
    ]
    for event_type, expected_style in style_contexts:
        event_context = VALID_EVENT_CONTEXT.copy()
        event_context["event_type"] = event_type
        request = {
            "user_profile": VALID_USER_PROFILE,
            "event_context": event_context
        }
        response = client.post("/api/generate/complete-outfit", json=request)
        assert response.status_code == 200
        data = response.json()
        outfit = data["outfit"]
        # Verify that the outfit style matches the event type
        assert outfit["formality_level"] >= (7 if expected_style == "formal" else 3)

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 