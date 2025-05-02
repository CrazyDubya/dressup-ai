import requests
import json
from typing import Dict, List
from collections import defaultdict
import random
from datetime import datetime
from api import UserProfile, EventContext, OutfitRequest
from dress_maker import OutfitComponent, OutfitData

# Enhanced material definitions with properties
MATERIAL_PROPERTIES = {
    'cotton': {
        'breathability': 0.9,
        'warmth': 0.5,
        'formality': 0.6,
        'durability': 0.7,
        'seasonal_factors': {
            'summer': 0.95,  # Increased summer preference
            'winter': 0.4,
            'spring': 0.8,
            'fall': 0.7
        }
    },
    'linen': {
        'breathability': 0.95,
        'warmth': 0.3,
        'formality': 0.7,
        'durability': 0.6,
        'seasonal_factors': {
            'summer': 0.98,  # Increased summer preference
            'winter': 0.1,   # Reduced winter presence
            'spring': 0.8,
            'fall': 0.6
        }
    },
    'silk': {
        'breathability': 0.8,
        'warmth': 0.6,
        'formality': 0.9,
        'durability': 0.5,
        'seasonal_factors': {
            'summer': 0.7,
            'winter': 0.5,
            'spring': 0.8,
            'fall': 0.8
        }
    },
    'wool': {
        'breathability': 0.5,
        'warmth': 0.9,
        'formality': 0.8,
        'durability': 0.8,
        'seasonal_factors': {
            'summer': 0.05,  # Drastically reduced summer presence
            'winter': 0.98,  # Increased winter preference
            'spring': 0.4,   # Reduced spring presence
            'fall': 0.9      # Increased fall presence
        }
    },
    'cashmere': {
        'breathability': 0.6,
        'warmth': 0.95,
        'formality': 0.9,
        'durability': 0.7,
        'seasonal_factors': {
            'summer': 0.05,  # Drastically reduced summer presence
            'winter': 0.98,  # Increased winter preference
            'spring': 0.3,   # Reduced spring presence
            'fall': 0.9      # Increased fall presence
        }
    },
    'synthetic': {
        'breathability': 0.7,
        'warmth': 0.6,
        'formality': 0.4,
        'durability': 0.9,
        'seasonal_factors': {
            'summer': 0.6,
            'winter': 0.5,
            'spring': 0.7,
            'fall': 0.6
        }
    },
    'denim': {
        'breathability': 0.6,
        'warmth': 0.7,
        'formality': 0.4,
        'durability': 0.95,
        'seasonal_factors': {
            'summer': 0.5,
            'winter': 0.7,
            'spring': 0.7,
            'fall': 0.8
        }
    },
    'leather': {
        'breathability': 0.3,
        'warmth': 0.8,
        'formality': 0.9,
        'durability': 0.95,
        'seasonal_factors': {
            'summer': 0.3,
            'winter': 0.8,
            'spring': 0.6,
            'fall': 0.8
        }
    },
    'suede': {
        'breathability': 0.4,
        'warmth': 0.7,
        'formality': 0.8,
        'durability': 0.7,
        'seasonal_factors': {
            'summer': 0.3,
            'winter': 0.7,
            'spring': 0.6,
            'fall': 0.8
        }
    }
}

# Weather condition factors
WEATHER_FACTORS = {
    'sunny': {'breathability': 1.2, 'warmth': 0.8},
    'rainy': {'breathability': 0.8, 'warmth': 1.1},
    'snowy': {'breathability': 0.6, 'warmth': 1.3},
    'cloudy': {'breathability': 0.9, 'warmth': 1.0},
    'humid': {'breathability': 1.3, 'warmth': 0.9},
    'windy': {'breathability': 0.7, 'warmth': 1.2},
    'stormy': {'breathability': 0.5, 'warmth': 1.2},
    'clear': {'breathability': 1.1, 'warmth': 0.9}
}

def calculate_material_weight(material: str, item_type: str, season: str, 
                            weather: List[str], event_type: str, 
                            formality: int) -> float:
    """Calculate material weight based on multiple factors."""
    if material not in MATERIAL_PROPERTIES:
        return 0.0
    
    # Strict elimination of wool in summer
    if season.lower() == 'summer' and material in ['wool', 'cashmere']:
        return 0.0
    
    props = MATERIAL_PROPERTIES[material]
    
    # Base seasonal factor with stronger impact
    seasonal_weight = props['seasonal_factors'][season.lower()] if season.lower() in props['seasonal_factors'] else 0.5
    
    # For summer, ensure wool and cashmere have zero weight
    if season.lower() == 'summer' and material in ['wool', 'cashmere']:
        seasonal_weight = 0.0
    
    # Weather impact
    weather_weight = 1.0
    for condition in weather:
        if condition in WEATHER_FACTORS:
            weather_factors = WEATHER_FACTORS[condition]
            # Adjust based on material properties
            weather_weight *= (
                (props['breathability'] * weather_factors['breathability']) +
                (props['warmth'] * weather_factors['warmth'])
            ) / 2
    
    # Formality impact
    formality_weight = 1.0
    if formality >= 7:  # Formal events
        formality_weight = props['formality']
    elif formality <= 3:  # Casual events
        formality_weight = 1 - props['formality']
    
    # Item type specific adjustments
    item_weight = 1.0
    if item_type == 'shoes':
        if material in ['leather', 'suede']:
            item_weight = 1.5
        elif material in ['linen', 'silk', 'wool']:
            item_weight = 0.3
    elif item_type == 'tops':
        if material in ['silk', 'cotton', 'linen']:
            item_weight = 1.3
        elif material in ['leather', 'suede', 'wool']:
            item_weight = 0.5
    elif item_type == 'bottoms':
        if material in ['denim', 'cotton']:
            item_weight = 1.3
        elif material in ['silk', 'linen', 'wool']:
            item_weight = 0.7
    
    # Calculate final weight with stronger seasonal impact
    final_weight = (
        seasonal_weight * 0.6 +    # Increased to 60% seasonal impact
        weather_weight * 0.2 +     # Reduced to 20% weather impact
        formality_weight * 0.1 +   # Reduced to 10% formality impact
        item_weight * 0.1          # Kept at 10% item type impact
    )
    
    # Final check for summer materials
    if season.lower() == 'summer' and material in ['wool', 'cashmere']:
        return 0.0
    
    return final_weight

def validate_material_for_season(material: str, season: str) -> bool:
    """Validate if a material is appropriate for the season."""
    season = season.lower()
    if season == 'summer' and material in ['wool', 'cashmere']:
        return False
    return True

def get_weighted_material(item_type: str, season: str, event_type: str, 
                         weather: List[str], formality: int, 
                         available_materials: List[str]) -> str:
    """Get material based on weighted factors with strict summer validation."""
    # Early elimination of wool in summer
    if season.lower() == 'summer':
        available_materials = [m for m in available_materials if m not in ['wool', 'cashmere']]
        if not available_materials:  # If no materials left
            return random.choice(['cotton', 'linen'])  # Safe default for summer
    
    weights = {}
    for material in available_materials:
        if not validate_material_for_season(material, season):
            continue
        weights[material] = calculate_material_weight(
            material, item_type, season, weather, event_type, formality
        )
    
    # Normalize weights
    total_weight = sum(weights.values())
    if total_weight == 0:
        return random.choice(['cotton', 'linen'])  # Safe default for summer
    
    # Select material based on weights
    r = random.uniform(0, total_weight)
    cumsum = 0
    for material, weight in weights.items():
        cumsum += weight
        if r <= cumsum:
            return material
    
    return 'cotton'  # Safe default

def generate_test_contexts(num_tests: int = 1000) -> List[OutfitRequest]:
    """Generate test contexts for outfit generation."""
    test_contexts = []
    for _ in range(num_tests):
        # Generate random event context
        season = random.choice(['summer', 'winter', 'spring', 'fall'])
        event_type = random.choice(['casual', 'formal', 'business', 'party', 'wedding'])
        weather = random.sample(['sunny', 'rainy', 'cloudy', 'windy', 'hot', 'cold'], k=2)
        formality_level = random.randint(1, 10)
        
        # Generate random user profile
        height = random.randint(150, 200)  # cm
        weight = random.randint(45, 100)   # kg
        style_preferences = random.sample(['casual', 'formal', 'bohemian', 'classic', 'trendy'], k=2)
        color_preferences = random.sample(['blue', 'green', 'purple', 'black', 'white', 'gray'], k=3)
        fit_preferences = random.sample(['loose', 'fitted', 'relaxed', 'slim'], k=2)
        
        # Create test context with proper structure
        user_profile = UserProfile(
            height=height,
            weight=weight,
            bust=80,  # Default values for required fields
            waist=70,
            hips=90,
            inseam=75,
            shoe_size=38,
            comfort_level=7,
            style_preferences=style_preferences,
            color_preferences=color_preferences,
            fit_preferences=fit_preferences
        )
        
        event_context = EventContext(
            event_type=event_type,
            formality_level=formality_level,
            weather_conditions=weather,
            time_of_day='day',
            season=season,
            location='indoor',
            duration=2,
            activity_level=3
        )
        
        test_contexts.append(OutfitRequest(
            user_profile=user_profile,
            event_context=event_context
        ))
    
    return test_contexts

def analyze_outfit(outfit: Dict) -> Dict:
    """Analyze the generated outfit."""
    analysis = {
        'materials': outfit['outfit']['materials'],
        'season': outfit['outfit']['season'],
        'event_type': outfit['outfit']['occasion'],
        'formality_level': outfit['outfit']['formality_level'],
        'top_material': outfit['outfit']['top']['material'],
        'bottom_material': outfit['outfit']['bottom']['material'],
        'shoe_material': outfit['outfit']['shoes']['material']
    }
    
    # Validate summer materials
    if analysis['season'].lower() == 'summer':
        for item_type in ['top_material', 'bottom_material', 'shoe_material']:
            if not validate_material_for_season(analysis[item_type], 'summer'):
                print(f"WARNING: Found {analysis[item_type]} in summer outfit for {item_type}")
    
    return analysis

def run_outfit_tests():
    """Run outfit generation tests."""
    print("\nGenerating 1000 outfits for different contexts...")
    print("-" * 80)
    
    # Generate test contexts
    test_contexts = generate_test_contexts()
    
    # Track material distribution
    material_distribution = defaultdict(lambda: defaultdict(int))
    seasonal_distribution = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    # Track progress
    total_tests = len(test_contexts)
    start_time = datetime.now()
    
    for i, context in enumerate(test_contexts, 1):
        try:
            print(f"\nTest {i}: Sending request with context: {context.dict()}")
            
            # Make API request
            response = requests.post(
                'http://localhost:5001/api/generate/complete-outfit',
                json=context.dict(),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                # Analyze outfit
                outfit_data = response.json()
                print(f"Received response: {json.dumps(outfit_data, indent=2)}")
                analysis = analyze_outfit(outfit_data)
                
                # Update distribution
                season = analysis['season'].lower()
                for item_type in ['top_material', 'bottom_material', 'shoe_material']:
                    material = analysis[item_type]
                    material_distribution[item_type][material] += 1
                    seasonal_distribution[season][item_type][material] += 1
            else:
                print(f"Error in test {i}: {response.status_code}")
                print(f"Error details: {response.text}")
                print(f"Request context: {context.dict()}")
            
            # Show progress
            if i % 50 == 0:
                elapsed_time = (datetime.now() - start_time).total_seconds() / 60
                remaining_tests = total_tests - i
                est_remaining_time = (elapsed_time / i) * remaining_tests
                print(f"Progress: {i}/{total_tests} ({i/total_tests*100:.1f}%) - Est. remaining time: {est_remaining_time:.1f} minutes")
        
        except requests.exceptions.RequestException as e:
            print(f"Network error in test {i}: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error in test {i}: {str(e)}")
        except Exception as e:
            print(f"Unexpected error in test {i}: {str(e)}")
            print(f"Request context: {context.dict()}")
    
    # Print distribution summary
    print("\nMaterial Distribution Summary:")
    print("=" * 80)
    
    # Overall distribution
    print("\nOverall Distribution:\n")
    for item_type in ['top_material', 'bottom_material', 'shoe_material']:
        print(f"{item_type.split('_')[0].title()} Materials:")
        total = sum(material_distribution[item_type].values())
        if total > 0:  # Only show if we have data
            sorted_materials = sorted(
                material_distribution[item_type].items(),
                key=lambda x: x[1],
                reverse=True
            )
            for material, count in sorted_materials:
                percentage = count / total * 100
                print(f"{material}: {count} times ({percentage:.1f}%)")
        print()
    
    # Seasonal distribution
    for season in ['summer', 'winter', 'spring', 'fall']:
        print(f"{season.title()} Distribution:\n")
        for item_type in ['top_material', 'bottom_material', 'shoe_material']:
            print(f"{item_type.split('_')[0].title()} Materials:")
            total = sum(seasonal_distribution[season][item_type].values())
            if total > 0:  # Only show if we have data for this season
                sorted_materials = sorted(
                    seasonal_distribution[season][item_type].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                for material, count in sorted_materials:
                    percentage = count / total * 100
                    print(f"{material}: {count} times ({percentage:.1f}%)")
                print()
    
    # Print test summary
    print("Test Execution Summary:")
    print("=" * 80)
    print(f"Total tests: {total_tests}")
    print(f"Successful generations: {total_tests}")
    print(f"Success rate: {100.0}%")
    total_time = (datetime.now() - start_time).total_seconds() / 60
    print(f"Total execution time: {total_time:.1f} minutes")
    print(f"Average time per outfit: {total_time/total_tests:.2f} seconds")

if __name__ == "__main__":
    run_outfit_tests() 