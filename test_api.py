import pytest
from fastapi.testclient import TestClient
from api import (
    app, UserProfile, EventContext, OutfitRequest,
    MATERIAL_COMBINATIONS, LEGWEAR_TYPES
)
from measurement_utils import BodyType, SpecialRequirement
import json
import random

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

def test_error_response_format():
    """Test that error responses follow the expected format."""
    # Test with invalid request format
    response = client.post("/api/generate/complete-outfit", json="invalid")
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "message" in data
    assert "request_id" in data

    # Test with missing required fields
    response = client.post("/api/generate/complete-outfit", json={})
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "message" in data
    assert "request_id" in data

def test_request_logging():
    """Test that requests are properly logged."""
    # Make a request and check the log file
    response = client.post("/api/generate/complete-outfit", json={
        "user_profile": VALID_USER_PROFILE,
        "event_context": VALID_EVENT_CONTEXT
    })
    assert response.status_code == 200
    
    # Check that the response includes a request_id
    data = response.json()
    assert "request_id" in data

def test_validation_error_handling():
    """Test handling of validation errors."""
    invalid_profile = VALID_USER_PROFILE.copy()
    invalid_profile["height"] = -1  # Invalid height
    
    response = client.post("/api/generate/complete-outfit", json={
        "user_profile": invalid_profile,
        "event_context": VALID_EVENT_CONTEXT
    })
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Validation error"
    assert "message" in data
    assert "request_id" in data

def test_material_selection_error():
    """Test handling of material selection errors."""
    invalid_context = VALID_EVENT_CONTEXT.copy()
    invalid_context["season"] = "invalid_season"
    
    response = client.post("/api/generate/complete-outfit", json={
        "user_profile": VALID_USER_PROFILE,
        "event_context": invalid_context
    })
    assert response.status_code == 500
    data = response.json()
    assert data["error"] == "Material selection error"
    assert "message" in data
    assert "request_id" in data

def test_dress_generation():
    """Test dress generation for formal events."""
    formal_context = VALID_EVENT_CONTEXT.copy()
    formal_context["formality_level"] = 8
    formal_context["event_type"] = "wedding"
    
    request = {
        "user_profile": VALID_USER_PROFILE,
        "event_context": formal_context
    }
    
    # Make multiple requests to increase chance of getting a dress
    for _ in range(5):
        response = client.post("/api/generate/complete-outfit", json=request)
        assert response.status_code == 200
        data = response.json()
        
        if "dress" in data["outfit"] and data["outfit"]["dress"] is not None:
            dress = data["outfit"]["dress"]
            assert dress["type"] == "dress"
            assert "length" in dress
            assert "neckline" in dress
            assert "sleeve_type" in dress
            assert dress["style"] in ["formal", "party"]
            return
    
    assert False, "No dress was generated in 5 attempts for a formal event"

def test_legwear_generation():
    """Test legwear generation for winter events."""
    winter_context = VALID_EVENT_CONTEXT.copy()
    winter_context["season"] = "winter"
    winter_context["formality_level"] = 6
    
    request = {
        "user_profile": VALID_USER_PROFILE,
        "event_context": winter_context
    }
    
    # Make multiple requests to increase chance of getting a dress with legwear
    for _ in range(5):
        response = client.post("/api/generate/complete-outfit", json=request)
        assert response.status_code == 200
        data = response.json()
        
        if "dress" in data["outfit"] and data["outfit"]["dress"] is not None:
            if "legwear" in data["outfit"] and data["outfit"]["legwear"] is not None:
                legwear = data["outfit"]["legwear"]
                assert legwear["type"] in ["stockings", "tights", "leggings"]
                assert legwear["material"] in ["nylon", "cotton", "wool"]
                return
    
    assert False, "No legwear was generated in 5 attempts for a winter event"

def test_summer_dress_no_legwear():
    """Test summer dress generation without legwear."""
    summer_context = VALID_EVENT_CONTEXT.copy()
    summer_context["season"] = "summer"
    summer_context["formality_level"] = 4
    
    request = {
        "user_profile": VALID_USER_PROFILE,
        "event_context": summer_context
    }
    
    # Make multiple requests to increase chance of getting a dress
    for _ in range(5):
        response = client.post("/api/generate/complete-outfit", json=request)
        assert response.status_code == 200
        data = response.json()
        
        if "dress" in data["outfit"] and data["outfit"]["dress"] is not None:
            assert data["outfit"]["legwear"] is None or data["outfit"]["legwear"]["type"] == "none"
            return
    
    assert False, "No summer dress was generated in 5 attempts"

def test_dress_legwear_combinations():
    """Test various dress and legwear combinations."""
    test_cases = [
        {
            "context": {
                "season": "winter",
                "formality_level": 7,
                "event_type": "formal"
            },
            "expected_legwear": ["stockings", "tights"]
        },
        {
            "context": {
                "season": "summer",
                "formality_level": 3,
                "event_type": "party"
            },
            "expected_legwear": ["fishnets", "none"]
        },
        {
            "context": {
                "season": "fall",
                "formality_level": 5,
                "event_type": "business"
            },
            "expected_legwear": ["tights", "leggings"]
        }
    ]
    
    for test_case in test_cases:
        context = VALID_EVENT_CONTEXT.copy()
        context.update(test_case["context"])
        
        request = {
            "user_profile": VALID_USER_PROFILE,
            "event_context": context
        }
        
        # Make multiple requests to increase chance of getting a dress
        for _ in range(5):
            response = client.post("/api/generate/complete-outfit", json=request)
            assert response.status_code == 200
            data = response.json()
            
            if "dress" in data["outfit"] and data["outfit"]["dress"] is not None:
                if "legwear" in data["outfit"] and data["outfit"]["legwear"] is not None:
                    legwear = data["outfit"]["legwear"]
                    assert legwear["type"] in test_case["expected_legwear"]
                    return
        
        assert False, f"No appropriate dress+legwear combination was generated in 5 attempts for {test_case['context']}"

def test_generate_1000_outfits():
    """Test generating 1000 outfits per season (4000 total) with various combinations of contexts."""
    # Define test scenarios with appropriate formality levels
    seasons = ["summer", "winter", "spring", "fall"]
    event_formality_map = {
        "wedding": (7, 9),  # Wedding requires formality 7-9
        "business_meeting": (5, 7),  # Business meeting requires formality 5-7
        "casual_gathering": (1, 3),  # Casual gathering allows formality 1-3
        "party": (3, 5)  # Party allows formality 3-5
    }
    event_types = list(event_formality_map.keys())
    
    # Statistics tracking
    stats = {
        "total_outfits": 0,
        "dress_count": 0,
        "top_bottom_count": 0,
        "seasonal_distribution": {season: 0 for season in seasons},
        "formality_distribution": {},
        "material_combinations": {},
        "event_type_distribution": {event: 0 for event in event_types},
        "seasonal_event_distribution": {season: {event: 0 for event in event_types} for season in seasons},
        "errors": []
    }
    
    # Generate 1000 outfits per season
    for season in seasons:
        print(f"\nGenerating outfits for {season}...")
        
        # Create a list of event types with even distribution for this season
        outfits_per_event = 1000 // len(event_types)
        remaining_outfits = 1000 % len(event_types)
        
        event_type_sequence = []
        for event_type in event_types:
            event_type_sequence.extend([event_type] * outfits_per_event)
        event_type_sequence.extend([event_types[0]] * remaining_outfits)
        random.shuffle(event_type_sequence)
        
        # Generate outfits for this season
        for event_type in event_type_sequence:
            min_formality, max_formality = event_formality_map[event_type]
            formality_level = random.randint(min_formality, max_formality)
            
            context = VALID_EVENT_CONTEXT.copy()
            context["season"] = season
            context["formality_level"] = formality_level
            context["event_type"] = event_type
            
            request = {
                "user_profile": VALID_USER_PROFILE,
                "event_context": context
            }
            
            try:
                response = client.post("/api/generate/complete-outfit", json=request)
                assert response.status_code == 200
                data = response.json()
                outfit = data["outfit"]
                
                # Update statistics
                stats["total_outfits"] += 1
                stats["seasonal_distribution"][season] += 1
                stats["event_type_distribution"][event_type] += 1
                stats["seasonal_event_distribution"][season][event_type] += 1
                
                # Track formality distribution
                formality = outfit["formality_level"]
                stats["formality_distribution"][formality] = stats["formality_distribution"].get(formality, 0) + 1
                
                # Track dress vs top+bottom distribution
                if outfit.get("dress"):
                    stats["dress_count"] += 1
                else:
                    stats["top_bottom_count"] += 1
                
                # Track material combinations
                materials = tuple(sorted(outfit["materials"]))
                stats["material_combinations"][materials] = stats["material_combinations"].get(materials, 0) + 1
                
                # Validate outfit structure
                assert "style_preferences" in outfit
                assert "color_preferences" in outfit
                assert "materials" in outfit
                assert "suitability" in outfit
                assert "occasion" in outfit
                assert "season" in outfit
                assert "formality_level" in outfit
                assert "comfort_level" in outfit
                assert "shoes" in outfit
                
                # Validate that either dress or top+bottom is present, not both
                assert (outfit.get("dress") is None) != (outfit.get("top") is None and outfit.get("bottom") is None)
                
                # Validate seasonal appropriateness
                for material in outfit["materials"]:
                    assert material in MATERIAL_COMBINATIONS[season], f"Invalid material {material} for {season}"
                
                # Validate formality level matches event type requirements
                assert outfit["formality_level"] >= min_formality, f"Formality level {outfit['formality_level']} too low for {event_type}"
                assert outfit["formality_level"] <= max_formality, f"Formality level {outfit['formality_level']} too high for {event_type}"
                
                # Validate legwear appropriateness
                if outfit.get("dress") and outfit.get("legwear"):
                    legwear = outfit["legwear"]
                    if legwear["type"] != "none":
                        assert legwear["type"] in LEGWEAR_TYPES
                        assert season in LEGWEAR_TYPES[legwear["type"]]["seasons"]
                
            except Exception as e:
                stats["errors"].append({
                    "context": context,
                    "error": str(e)
                })
    
    # Print statistics
    print("\nOutfit Generation Statistics:")
    print(f"Total outfits generated: {stats['total_outfits']}")
    print(f"Dress outfits: {stats['dress_count']} ({stats['dress_count']/stats['total_outfits']*100:.1f}%)")
    print(f"Top+Bottom outfits: {stats['top_bottom_count']} ({stats['top_bottom_count']/stats['total_outfits']*100:.1f}%)")
    
    print("\nSeasonal Distribution:")
    for season, count in stats["seasonal_distribution"].items():
        print(f"{season}: {count} ({count/stats['total_outfits']*100:.1f}%)")
    
    print("\nEvent Type Distribution (Overall):")
    for event_type, count in stats["event_type_distribution"].items():
        print(f"{event_type}: {count} ({count/stats['total_outfits']*100:.1f}%)")
    
    print("\nEvent Type Distribution by Season:")
    for season in seasons:
        print(f"\n{season.title()}:")
        for event_type, count in stats["seasonal_event_distribution"][season].items():
            print(f"  {event_type}: {count} ({count/1000*100:.1f}%)")
    
    print("\nFormality Level Distribution:")
    for level, count in sorted(stats["formality_distribution"].items()):
        print(f"Level {level}: {count} ({count/stats['total_outfits']*100:.1f}%)")
    
    print("\nTop 5 Material Combinations:")
    sorted_combinations = sorted(stats["material_combinations"].items(), key=lambda x: x[1], reverse=True)
    for materials, count in sorted_combinations[:5]:
        print(f"{materials}: {count} ({count/stats['total_outfits']*100:.1f}%)")
    
    if stats["errors"]:
        print("\nErrors encountered:")
        for error in stats["errors"]:
            print(f"Context: {error['context']}")
            print(f"Error: {error['error']}\n")
    
    # Assertions
    assert stats["total_outfits"] == 4000, "Did not generate 4000 outfits"
    assert len(stats["errors"]) == 0, f"Encountered {len(stats['errors'])} errors during generation"
    
    # Verify reasonable distribution of dress vs top+bottom
    dress_ratio = stats["dress_count"] / stats["total_outfits"]
    assert 0.2 <= dress_ratio <= 0.8, f"Unreasonable dress ratio: {dress_ratio}"
    
    # Verify each season has exactly 1000 outfits
    for season, count in stats["seasonal_distribution"].items():
        assert count == 1000, f"Wrong number of outfits for {season}: {count} (expected 1000)"
    
    # Verify event type distribution within each season
    expected_event_count = 1000 // len(event_types)
    for season in seasons:
        for event_type, count in stats["seasonal_event_distribution"][season].items():
            assert abs(count - expected_event_count) <= 1, \
                f"Uneven distribution for {event_type} in {season}: {count} (expected {expected_event_count})"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 