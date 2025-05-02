import unittest
from web_app.dress_maker import (
    OutfitGenerator, StyleAnalyzer, OutfitCombinationEngine,
    CulturalValidator, SeasonalAdapter
)
from typing import Dict, List, Set
import json
import os
import tempfile
import shutil
from web_app.user_profile import UserProfile, Measurements, PhysicalFeatures, StylePreferences, StylePreference, MeasurementUnit, BustMeasurement, CupSize
from flask import Flask
from pathlib import Path

class TestEnhancedDressMaker(unittest.TestCase):
    def setUp(self):
        self.outfit_generator = OutfitGenerator()
        self.style_analyzer = StyleAnalyzer()
        self.combination_engine = OutfitCombinationEngine()
        self.cultural_validator = CulturalValidator()
        self.seasonal_adapter = SeasonalAdapter()

    def test_dynamic_prompt_generation(self):
        """Test the generation of dynamic prompts for different events."""
        events = ['wedding', 'business', 'casual', 'date', 'party', 'beach', 'gym']
        for event in events:
            prompt = self.outfit_generator.generate_outfit_prompt(event, 1, 1)
            self.assertIsInstance(prompt, str)
            self.assertGreater(len(prompt), 0)
            self.assertIn(event.lower(), prompt.lower())

    def test_style_analysis(self):
        """Test the style analysis functionality."""
        descriptions = [
            "A professional business suit with a white blouse",
            "A flowy bohemian dress with floral patterns",
            "An edgy leather jacket with ripped jeans"
        ]
        for desc in descriptions:
            styles = self.style_analyzer.analyze_description(desc)
            self.assertIsInstance(styles, Set)
            self.assertGreater(len(styles), 0)

    def test_variation_styles(self):
        """Test that prompts include different variation styles."""
        variation_styles = ["seductive", "conservative", "provocative", "playful", "flirty"]
        for i in range(1, 6):
            prompt = self.outfit_generator.generate_outfit_prompt('date', 1, i)
            self.assertIsInstance(prompt, str)
            self.assertGreater(len(prompt), 0)

    def test_rich_event_contexts(self):
        """Test the inclusion of rich event contexts in prompts."""
        events = {
            'wedding': 'opulent celebration',
            'interview': 'high-stakes moment',
            'date': 'intimate rendezvous',
            'casual': 'sunlit afternoon',
            'business': 'bustling corporate setting',
            'party': 'vibrant soirée',
            'beach': 'breezy coastal escape',
            'gym': 'active environment'
        }
        for event, context in events.items():
            prompt = self.outfit_generator.generate_outfit_prompt(event, 1, 1)
            self.assertIsInstance(prompt, str)
            self.assertGreater(len(prompt), 0)

    def test_example_responses(self):
        """Test the rotation of example responses."""
        outfits = []
        for i in range(1, 4):
            prompt = self.outfit_generator.generate_outfit_prompt('date', i, 1)
            outfits.append(prompt)
        # Verify that different example responses are used
        self.assertNotEqual(outfits[0], outfits[1])
        self.assertNotEqual(outfits[1], outfits[2])

    def test_outfit_generation(self):
        """Test the complete outfit generation process."""
        event = 'date'
        num_outfits = 2
        variations = 2
        outfits = self.outfit_generator.generate_outfit(event, num_outfits, variations)
        self.assertIsInstance(outfits, List)
        self.assertEqual(len(outfits), num_outfits * variations)
        for outfit in outfits:
            self.assertIsInstance(outfit, Dict)
            self.assertIn('top', outfit)
            self.assertIn('bottom', outfit)
            self.assertIn('shoes', outfit)
            self.assertIn('extras', outfit)

    def test_preferences_integration(self):
        """Test the integration of user preferences."""
        preferences = {
            'colors': ['blue', 'black'],
            'materials': ['cotton', 'silk'],
            'styles': ['professional', 'casual']
        }
        outfits = self.outfit_generator.generate_outfit('business', 1, 1, preferences)
        self.assertIsInstance(outfits, List)
        for outfit in outfits:
            self.assertIsInstance(outfit, Dict)
            outfit_text = ' '.join(str(v) for v in outfit.values()).lower()
            # Pass if at least one preferred color and one preferred material is present
            color_found = any(color.lower() in outfit_text for color in preferences['colors'])
            material_found = any(material.lower() in outfit_text for material in preferences['materials'])
            self.assertTrue(color_found, f"None of the preferred colors found in: {outfit_text}")
            self.assertTrue(material_found, f"None of the preferred materials found in: {outfit_text}")

    def test_outfit_combinations(self):
        """Test the outfit combination engine."""
        base_outfit = {
            'features': {
                'styles': ['casual'],
                'colors': ['blue'],
                'materials': ['cotton']
            },
            'components': {
                'top': 'blue cotton t-shirt',
                'bottom': 'jeans',
                'shoes': 'sneakers'
            }
        }
        
        combinations = self.combination_engine.suggest_combinations(base_outfit)
        self.assertIsInstance(combinations, List)
        self.assertGreater(len(combinations), 0)
        
        for combo in combinations:
            self.assertIn('type', combo)
            self.assertIn('base_outfit', combo)
            self.assertIn('suggested_changes', combo)
            self.assertIn('reasoning', combo)

    def test_cultural_validation(self):
        """Test the cultural validation system."""
        outfit_data = {
            'features': {
                'styles': ['fantasy'],
                'materials': ['silk', 'velvet'],
                'colors': ['royal blue', 'gold']
            },
            'components': {
                'top': 'royal blue velvet tunic',
                'bottom': 'silk trousers',
                'shoes': 'leather boots'
            }
        }
        
        validation = self.cultural_validator.validate_outfit(
            outfit_data,
            'fantasy',
            'medieval'
        )
        
        self.assertIsInstance(validation, Dict)
        self.assertIn('is_valid', validation)
        self.assertIn('suggestions', validation)
        self.assertIn('cultural_score', validation)
        self.assertIn('historical_score', validation)

    def test_seasonal_adaptation(self):
        """Test the seasonal adaptation system."""
        outfit_data = {
            'features': {
                'materials': ['cotton'],
                'lengths': ['short']
            },
            'components': {
                'top': 'cotton t-shirt',
                'bottom': 'shorts',
                'shoes': 'sandals'
            }
        }
        
        adaptation = self.seasonal_adapter.adapt_outfit(
            outfit_data,
            'winter',
            'snow'
        )
        
        self.assertIsInstance(adaptation, Dict)
        self.assertIn('seasonal_score', adaptation)
        self.assertIn('suggestions', adaptation)
        self.assertIn('is_seasonally_appropriate', adaptation)

    def test_integrated_outfit_generation(self):
        """Test the complete outfit generation with all enhancements."""
        event = 'business'
        num_outfits = 1
        variations = 1
        
        outfits = self.outfit_generator.generate_outfit(
            event,
            num_outfits,
            variations,
            is_character_outfit=False,
            real_world_context={
                'season': 'winter',
                'weather': 'snow'
            }
        )
        
        self.assertIsInstance(outfits, List)
        self.assertEqual(len(outfits), num_outfits * variations)
        
        for outfit in outfits:
            self.assertIn('top', outfit)
            self.assertIn('bottom', outfit)
            self.assertIn('shoes', outfit)
            self.assertIn('extras', outfit)

class TestProfileFields(unittest.TestCase):
    def setUp(self):
        # Use a temp directory for user data
        self.temp_dir = tempfile.mkdtemp()
        self.user_profile = UserProfile()
        self.user_profile.base_dir = Path(self.temp_dir)
        self.user_profile._ensure_directories()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_save_and_load_profile_with_shoe_and_cup_fields(self):
        name = "TestUser"
        bust = BustMeasurement(band_size=34, cup_size=CupSize.D, unit=MeasurementUnit.INCHES)
        measurements = Measurements(
            height=66,
            height_unit=MeasurementUnit.INCHES,
            weight=140,
            weight_unit=MeasurementUnit.LBS,
            bust=bust,
            waist=28,
            hips=38,
            inseam=30,
            shoulder_width=16,
            arm_length=24,
            shoe_size=8.5,
            shoe_size_unit="us",
            max_heel_height=3.5,
            shoe_width="medium"
        )
        physical_features = PhysicalFeatures(
            eye_color="blue",
            hair_color="brown",
            hair_length="long",
            skin_tone="fair",
            body_type="hourglass"
        )
        style_preferences = StylePreferences(
            primary_style=StylePreference.CLASSIC,
            secondary_styles={StylePreference.ROMANTIC, StylePreference.CASUAL},
            favorite_colors={"blue", "white"},
            favorite_materials={"cotton", "silk"},
            preferred_silhouettes={"a_line", "fitted"},
            style_adaptability=7,
            comfort_priority=8,
            modesty_level=5,
            color_preferences={},
            material_preferences={},
            style_restrictions=None,
            seasonal_preferences=None,
            preferred_heel_height=["medium", "high"],
            shoe_styles=["open_toe", "sandals"]
        )
        self.user_profile.create_profile(name, measurements, physical_features, style_preferences)
        loaded = self.user_profile.get_profile(name)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded['measurements']['shoe_size'], 8.5)
        self.assertEqual(loaded['measurements']['shoe_size_unit'], "us")
        self.assertEqual(loaded['measurements']['max_heel_height'], 3.5)
        self.assertEqual(loaded['measurements']['shoe_width'], "medium")
        self.assertEqual(loaded['measurements']['bust']['band_size'], 34)
        self.assertEqual(loaded['measurements']['bust']['cup_size'], "D")
        self.assertIn("medium", loaded['style_preferences']['preferred_heel_height'])
        self.assertIn("high", loaded['style_preferences']['preferred_heel_height'])
        self.assertIn("open_toe", loaded['style_preferences']['shoe_styles'])
        self.assertIn("sandals", loaded['style_preferences']['shoe_styles'])

if __name__ == '__main__':
    unittest.main() 