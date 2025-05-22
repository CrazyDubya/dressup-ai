import unittest
from dress_maker import DressMaker, OutfitData, OutfitComponent
import json
from datetime import datetime

class TestDressMaker(unittest.TestCase):
    def setUp(self):
        self.dress_maker = DressMaker()
        self.test_user_profile = {
            'height': 165,
            'weight': 60,
            'bust': 85,
            'cup_size': 'B',
            'waist': 70,
            'hips': 90,
            'shoulder_width': 38,
            'arm_length': 58,
            'username': 'test_user',
            'shoe_size': 38,
            'heel_height_preference': 7,
            'heel_width_preference': 'narrow',
            'open_toe_preference': True,
            'comfort_priority': 1
        }
        self.test_event_context = {
            'type': 'casual',
            'formality': 3,
            'season': 'summer',
            'location': 'outdoor',
            'user_profile': self.test_user_profile
        }

    def test_generate_casual_outfit(self):
        """Test generating a casual outfit with user preferences."""
        outfits = self.dress_maker.generate_outfit(
            event='casual',
            num_outfits=1,
            variations_per_outfit=1,
            real_world_context=self.test_event_context
        )
        
        self.assertTrue(len(outfits) > 0)
        outfit = outfits[0]
        
        # Check required components
        self.assertIn('top', outfit)
        self.assertIn('bottom', outfit)
        self.assertIn('shoes', outfit)
        
        # Check shoes match preferences
        shoes = outfit['shoes']
        self.assertIn('heel_height', shoes)
        self.assertIn('heel_width', shoes)
        self.assertIn('open_toe', shoes)
        self.assertIn('comfort_level', shoes)
        
        # Verify shoe preferences are respected
        self.assertTrue(abs(shoes['heel_height'] - self.test_user_profile['heel_height_preference']) <= 2)
        self.assertEqual(shoes['heel_width'], self.test_user_profile['heel_width_preference'])
        self.assertEqual(shoes['open_toe'], self.test_user_profile['open_toe_preference'])
        
        # Check comfort level is adjusted based on priority
        self.assertTrue(shoes['comfort_level'] <= 5)  # Should be low due to comfort_priority=1

    def test_generate_formal_outfit(self):
        """Test generating a formal outfit with user preferences."""
        formal_context = self.test_event_context.copy()
        formal_context['type'] = 'formal'
        formal_context['formality'] = 8
        
        outfits = self.dress_maker.generate_outfit(
            event='formal',
            num_outfits=1,
            variations_per_outfit=1,
            real_world_context=formal_context
        )
        
        self.assertTrue(len(outfits) > 0)
        outfit = outfits[0]
        
        # Check required components
        self.assertIn('top', outfit)
        self.assertIn('bottom', outfit)
        self.assertIn('shoes', outfit)
        
        # Check shoes match preferences
        shoes = outfit['shoes']
        self.assertIn('heel_height', shoes)
        self.assertIn('heel_width', shoes)
        self.assertIn('open_toe', shoes)
        self.assertIn('comfort_level', shoes)
        
        # Verify shoe preferences are respected
        self.assertTrue(abs(shoes['heel_height'] - self.test_user_profile['heel_height_preference']) <= 2)
        self.assertEqual(shoes['heel_width'], self.test_user_profile['heel_width_preference'])
        self.assertEqual(shoes['open_toe'], self.test_user_profile['open_toe_preference'])
        
        # Check comfort level is adjusted based on priority
        self.assertTrue(shoes['comfort_level'] <= 5)  # Should be low due to comfort_priority=1

    def test_outfit_validation(self):
        """Test outfit validation."""
        # Test valid outfit
        valid_outfit = {
            'top': {'description': 'Test top'},
            'bottom': {'description': 'Test bottom'},
            'shoes': {'description': 'Test shoes'}
        }
        self.assertTrue(self.dress_maker._validate_outfit_data(valid_outfit))
        
        # Test invalid outfit (missing components)
        invalid_outfit = {
            'top': {'description': 'Test top'},
            'bottom': {'description': 'Test bottom'}
        }
        self.assertFalse(self.dress_maker._validate_outfit_data(invalid_outfit))

def test_outfit_generation():
    # Initialize DressMaker
    maker = DressMaker()
    
    # Test cases with different scenarios
    test_cases = [
        {
            "name": "Formal Evening Gala",
            "event": "gala",
            "num_outfits": 1,
            "variations": 1,
            "real_world_context": {
                "user_profile": {
                    "preferred_materials": ["silk", "lace"],
                    "favorite_colors": ["black", "emerald"],
                    "style_preferences": ["elegant", "dramatic"]
                },
                "season": "winter",
                "formality": 9
            }
        },
        {
            "name": "Casual Garden Party",
            "event": "garden party",
            "num_outfits": 1,
            "variations": 1,
            "real_world_context": {
                "user_profile": {
                    "preferred_materials": ["cotton", "linen"],
                    "favorite_colors": ["pastel pink", "mint green"],
                    "style_preferences": ["feminine", "delicate"]
                },
                "season": "spring",
                "formality": 4
            }
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        print(f"\nGenerating outfit for: {test_case['name']}")
        try:
            outfits = maker.generate_outfit(
                event=test_case['event'],
                num_outfits=test_case['num_outfits'],
                variations_per_outfit=test_case['variations'],
                real_world_context=test_case['real_world_context']
            )
            
            # Convert outfits to dict for JSON serialization
            outfit_dicts = []
            for outfit in outfits:
                outfit_dict = outfit.model_dump()
                outfit_dicts.append(outfit_dict)
            
            results[test_case['name']] = outfit_dicts
            print(f"Successfully generated outfit for {test_case['name']}")
            
        except Exception as e:
            print(f"Error generating outfit for {test_case['name']}: {str(e)}")
            results[test_case['name']] = {"error": str(e)}
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"dress_maker_test_results_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nTest results saved to {filename}")
    return results

if __name__ == "__main__":
    test_outfit_generation() 