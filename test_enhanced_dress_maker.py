import json
from datetime import datetime
from dress_maker import DressMaker, UserProfile, WeatherContext

def test_enhanced_outfit_generation():
    # Initialize dress maker
    dress_maker = DressMaker()
    
    # Create test user profiles with different body shapes and preferences
    user_profiles = [
        UserProfile(
            user_id="test_user_001",
            name="Emma Smith",
            body_shape="pear",
            favorite_colors=["emerald", "navy", "black"],
            preferred_materials=["silk", "wool"],
            style_preferences=["elegant", "structured"],
            budget_range={"min": 500, "max": 2000}
        ),
        UserProfile(
            user_id="test_user_002",
            name="Sophie Chen",
            body_shape="hourglass",
            favorite_colors=["coral", "mint green", "white"],
            preferred_materials=["cotton", "linen"],
            style_preferences=["comfortable", "feminine"],
            budget_range={"min": 200, "max": 800}
        ),
        UserProfile(
            user_id="test_user_003",
            name="Maria Garcia",
            body_shape="apple",
            favorite_colors=["black", "navy", "nude"],
            preferred_materials=["wool", "leather"],
            style_preferences=["professional", "polished"],
            budget_range={"min": 1000, "max": 3000}
        ),
        # Add edge case test user
        UserProfile(
            user_id="test_user_004",
            name="Alex Frost",
            body_shape="rectangle",
            favorite_colors=["silver"],  # Limited color preference
            preferred_materials=["wool"],  # Will conflict with allergy
            style_preferences=["sporty"],
            budget_range={"min": 50, "max": 100},  # Very low budget
        )
    ]
    
    # Save user profiles
    for profile in user_profiles:
        dress_maker.save_user_profile(profile)
    
    # Create different weather contexts
    weather_contexts = {
        "london_winter": WeatherContext(
            temperature=5.0,
            condition="rainy",
            humidity=0.8,
            wind_speed=15.0,
            location="London",
            date=datetime.now()
        ),
        "miami_summer": WeatherContext(
            temperature=30.0,
            condition="sunny",
            humidity=0.7,
            wind_speed=8.0,
            location="Miami",
            date=datetime.now()
        ),
        "paris_spring": WeatherContext(
            temperature=18.0,
            condition="partly_cloudy",
            humidity=0.6,
            wind_speed=12.0,
            location="Paris",
            date=datetime.now()
        ),
        # Add extreme weather contexts
        "arctic_blizzard": WeatherContext(
            temperature=-15.0,
            condition="blizzard",
            humidity=0.9,
            wind_speed=40.0,
            location="Reykjavik",
            date=datetime.now()
        ),
        "desert_heatwave": WeatherContext(
            temperature=47.0,
            condition="heatwave",
            humidity=0.1,
            wind_speed=5.0,
            location="Dubai",
            date=datetime.now()
        ),
        "hurricane": WeatherContext(
            temperature=25.0,
            condition="hurricane",
            humidity=0.95,
            wind_speed=120.0,
            location="Miami",
            date=datetime.now()
        )
    }
    
    # Test cases combining different users, events, and weather conditions
    test_cases = [
        {
            "name": "Winter Gala in London",
            "event": "gala",
            "user": user_profiles[0],  # Emma - pear shape
            "weather": weather_contexts["london_winter"],
            "real_world_context": {
                "season": "winter",
                "formality": 9,
                "time_of_day": "evening"
            }
        },
        {
            "name": "Summer Garden Party in Miami",
            "event": "garden party",
            "user": user_profiles[1],  # Sophie - hourglass shape
            "weather": weather_contexts["miami_summer"],
            "real_world_context": {
                "season": "summer",
                "formality": 5,
                "time_of_day": "afternoon"
            }
        },
        {
            "name": "Spring Business Conference in Paris",
            "event": "business",
            "user": user_profiles[2],  # Maria - apple shape
            "weather": weather_contexts["paris_spring"],
            "real_world_context": {
                "season": "spring",
                "formality": 7,
                "time_of_day": "morning"
            }
        },
        {
            "name": "Winter Wedding Guest in London",
            "event": "wedding",
            "user": user_profiles[1],  # Sophie - hourglass shape
            "weather": weather_contexts["london_winter"],
            "real_world_context": {
                "season": "winter",
                "formality": 8,
                "time_of_day": "afternoon"
            }
        },
        # Add edge case test scenarios
        {
            "name": "Arctic Blizzard Expedition",
            "event": "expedition",
            "user": user_profiles[3],  # Alex - rectangle shape, low budget
            "weather": weather_contexts["arctic_blizzard"],
            "real_world_context": {
                "season": "winter",
                "formality": 2,
                "time_of_day": "morning",
                "allergies": ["wool"]  # Conflicting with preferred material
            }
        },
        {
            "name": "Desert Heatwave Trek",
            "event": "trekking",
            "user": user_profiles[3],  # Alex - rectangle shape, low budget
            "weather": weather_contexts["desert_heatwave"],
            "real_world_context": {
                "season": "summer",
                "formality": 1,
                "time_of_day": "afternoon"
            }
        },
        {
            "name": "Hurricane Emergency Response",
            "event": "emergency",
            "user": user_profiles[3],  # Alex - rectangle shape, low budget
            "weather": weather_contexts["hurricane"],
            "real_world_context": {
                "season": "summer",
                "formality": 1,
                "time_of_day": "morning",
                "safety_requirements": ["waterproof", "high_visibility"]
            }
        }
    ]
    
    # Generate outfits for each test case
    results = {}
    for test_case in test_cases:
        print(f"\nGenerating outfit for: {test_case['name']}")
        print(f"User: {test_case['user'].name} ({test_case['user'].body_shape})")
        print(f"Weather: {test_case['weather'].condition}, {test_case['weather'].temperature}°C in {test_case['weather'].location}")
        
        # Prepare context with all relevant information
        context = {
            "user_id": test_case["user"].user_id,
            "weather": test_case["weather"].model_dump(),
            **test_case["real_world_context"]
        }
        
        outfits = dress_maker.generate_outfit(
            event=test_case["event"],
            num_outfits=1,
            variations_per_outfit=2,  # Generate two variations
            real_world_context=context
        )
        
        if outfits:
            # Convert to dict for JSON serialization
            results[test_case["name"]] = [outfit.model_dump() for outfit in outfits]
            
            # Add feedback for each outfit
            for i, outfit in enumerate(outfits):
                feedback = {
                    "outfit_id": f"{test_case['event']}_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "user_id": test_case["user"].user_id,
                    "rating": 5,
                    "comments": f"Perfect for {test_case['name']}!"
                }
                dress_maker.add_outfit_feedback(feedback)
    
    # Save results with detailed metadata
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"enhanced_outfit_test_results_{timestamp}.json"
    
    # Add metadata to results
    final_results = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "test_cases": len(test_cases),
            "total_outfits": sum(len(outfits) for outfits in results.values()),
            "weather_conditions": [w.condition for w in weather_contexts.values()],
            "user_profiles": [{"id": p.user_id, "body_shape": p.body_shape} for p in user_profiles]
        },
        "outfits": results
    }
    
    with open(output_file, 'w') as f:
        json.dump(final_results, f, indent=2, default=str)
    
    print(f"\nTest results saved to {output_file}")
    
    # Display outfit history for each user
    for profile in user_profiles:
        history = dress_maker.get_outfit_history(profile.user_id)
        print(f"\nOutfit history for {profile.name} ({profile.user_id}):")
        for outfit in history:
            print(f"- {outfit.outfit_id}: {outfit.outfit_data.get('occasion', 'Unknown')}")

if __name__ == "__main__":
    test_enhanced_outfit_generation() 
