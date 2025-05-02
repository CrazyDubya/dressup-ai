"""
Command-line interface for managing user profiles and generating personalized outfits.
"""

import sys
import logging
from typing import Optional, Dict, List
from user_profile import (
    UserProfile, Measurements, PhysicalFeatures, StylePreferences,
    MeasurementUnit, StylePreference, BustMeasurement, CupSize
)
from dress_maker import OutfitGenerator
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserInterface:
    def __init__(self):
        self.outfit_generator = OutfitGenerator()
        self.user_profile = UserProfile()
        self.current_user: Optional[str] = None
    
    def _get_valid_float(self, prompt: str) -> Optional[float]:
        """Get a valid float input from user."""
        while True:
            try:
                value = input(prompt)
                if not value:  # Allow empty input
                    return None
                return float(value)
            except ValueError:
                print("Please enter a valid number.")
    
    def _get_valid_cup_size(self) -> Optional[CupSize]:
        """Get a valid cup size from user."""
        print("Available cup sizes:", ", ".join(cup.value for cup in CupSize))
        while True:
            cup_size = input("Cup size: ").upper()
            try:
                return CupSize(cup_size)
            except ValueError:
                print("Please enter a valid cup size from the list above.")
    
    def _get_valid_rating(self, prompt: str, min_value: int = 1, max_value: int = 10) -> int:
        """Get a valid rating input from user (1-10)."""
        while True:
            try:
                value = input(prompt)
                rating = int(value)
                if min_value <= rating <= max_value:
                    return rating
                print(f"Please enter a number between {min_value} and {max_value}.")
            except ValueError:
                print("Please enter a valid number.")
    
    def login(self) -> bool:
        """Handle user login or registration."""
        print("\n=== Welcome to Fashion Outfit Generator ===")
        name = input("Enter your name: ")
        
        if self.user_profile.is_new_user(name):
            print(f"\nWelcome, {name}! Let's create your profile.")
            self.create_user_profile(name)
        else:
            print(f"\nWelcome back, {name}!")
            profile = self.user_profile.load_profile(name)
            if not profile:
                print("Error loading profile. Please try again.")
                return False
            
            # Display user stats
            outfit_count = self.user_profile.get_outfit_count(name)
            print(f"You have generated {outfit_count} outfits so far.")
            
            # Show recent style history
            style_history = self.user_profile.get_style_history(name)
            if style_history:
                print("\nYour recent outfits:")
                for outfit in style_history[-3:]:  # Show last 3 outfits
                    print(f"- {outfit['event']} ({outfit['created_at']})")
        
        self.current_user = name
        return True
    
    def create_user_profile(self, name: str) -> None:
        """Create a new user profile with measurements and preferences."""
        print("\n=== Create New User Profile ===")
        
        # Get measurements
        print("\nEnter your measurements:")
        height = self._get_valid_float("Height: ")
        height_unit = input("Unit (inches/cm): ").lower()
        weight = self._get_valid_float("Weight: ")
        weight_unit = input("Unit (lbs/kg/stone): ").lower()
        
        # Convert units to enum
        height_unit_enum = MeasurementUnit.INCHES if height_unit == "inches" else MeasurementUnit.CM
        weight_unit_enum = (
            MeasurementUnit.LBS if weight_unit == "lbs"
            else MeasurementUnit.KG if weight_unit == "kg"
            else MeasurementUnit.STONE
        )
        
        # Get optional measurements
        print("\nOptional measurements (press Enter to skip):")
        
        # Handle bust measurement with cup size
        print("\nBust measurement:")
        use_cup_size = input("Would you like to enter cup size? (y/n): ").lower() == 'y'
        if use_cup_size:
            band_size = self._get_valid_float("Band size: ")
            if band_size is not None:
                cup_size = self._get_valid_cup_size()
                if cup_size is not None:
                    bust = BustMeasurement(
                        band_size=band_size,
                        cup_size=cup_size,
                        unit=MeasurementUnit.INCHES
                    )
                else:
                    bust = None
            else:
                bust = None
        else:
            bust = self._get_valid_float("Bust (inches): ")
        
        # Get other measurements
        waist = self._get_valid_float("Waist: ")
        hips = self._get_valid_float("Hips: ")
        inseam = self._get_valid_float("Inseam: ")
        shoulder_width = self._get_valid_float("Shoulder width: ")
        arm_length = self._get_valid_float("Arm length: ")
        
        # Create measurements object
        measurements = Measurements(
            height=height,
            height_unit=height_unit_enum,
            weight=weight,
            weight_unit=weight_unit_enum,
            bust=bust,
            waist=waist,
            hips=hips,
            inseam=inseam,
            shoulder_width=shoulder_width,
            arm_length=arm_length
        )
        
        # Get physical features
        print("\nEnter your physical features:")
        eye_color = input("Eye color: ")
        hair_color = input("Hair color: ")
        hair_length = input("Hair length: ")
        skin_tone = input("Skin tone: ")
        body_type = input("Body type: ")
        face_shape = input("Face shape (optional): ")
        distinguishing_features = input("Distinguishing features (comma-separated, optional): ")
        
        physical_features = PhysicalFeatures(
            eye_color=eye_color,
            hair_color=hair_color,
            hair_length=hair_length,
            skin_tone=skin_tone,
            body_type=body_type,
            face_shape=face_shape if face_shape else None,
            distinguishing_features=distinguishing_features.split(",") if distinguishing_features else None
        )
        
        # Get style preferences
        print("\nEnter your style preferences:")
        print("Available styles:", ", ".join(style.value for style in StylePreference))
        primary_style = input("Primary style: ").lower()
        secondary_styles = input("Secondary styles (comma-separated): ").lower().split(",")
        
        print("\nEnter your favorite colors (comma-separated):")
        favorite_colors = input().split(",")
        
        print("\nEnter your favorite materials (comma-separated):")
        favorite_materials = input().split(",")
        
        print("\nEnter your preferred silhouettes (comma-separated):")
        preferred_silhouettes = input().split(",")
        
        print("\nRate your preferences (1-10):")
        style_adaptability = self._get_valid_rating("Style adaptability: ")
        comfort_priority = self._get_valid_rating("Comfort priority: ")
        modesty_level = self._get_valid_rating("Modesty level: ")
        
        # Create style preferences
        style_preferences = StylePreferences(
            primary_style=StylePreference(primary_style),
            secondary_styles={StylePreference(style.strip()) for style in secondary_styles},
            favorite_colors=set(favorite_colors),
            favorite_materials=set(favorite_materials),
            preferred_silhouettes=set(preferred_silhouettes),
            style_adaptability=style_adaptability,
            comfort_priority=comfort_priority,
            modesty_level=modesty_level,
            color_preferences={},  # Will be populated later
            material_preferences={},  # Will be populated later
            style_restrictions=None,
            seasonal_preferences=None
        )
        
        # Create the profile
        self.user_profile.create_profile(name, measurements, physical_features, style_preferences)
        print(f"\nProfile created successfully for {name}!")
    
    def rate_outfit(self, outfit: Dict) -> None:
        """Allow user to rate an outfit."""
        print("\nRate this outfit (1-10):")
        print(f"Top: {outfit['top']}")
        print(f"Bottom: {outfit['bottom']}")
        print(f"Shoes: {outfit['shoes']}")
        if outfit.get('extras'):
            print(f"Extras: {outfit['extras']}")
        
        # Get ratings for different aspects
        style_rating = self._get_valid_rating("Style rating (1-10): ")
        comfort_rating = self._get_valid_rating("Comfort rating (1-10): ")
        overall_rating = self._get_valid_rating("Overall rating (1-10): ")
        
        # Add ratings to outfit data
        outfit['user_ratings'] = {
            'style': style_rating,
            'comfort': comfort_rating,
            'overall': overall_rating,
            'rated_at': datetime.now().isoformat()
        }
        
        # Update outfit in user's history
        self.user_profile.update_outfit_rating(self.current_user, outfit['outfit_id'], outfit['user_ratings'])
        print("\nThank you for your rating!")

    def generate_personalized_outfit(self) -> None:
        """Generate a personalized outfit based on user profile."""
        if not self.current_user:
            print("Please login first.")
            return
        
        print("\n=== Generate Personalized Outfit ===")
        
        # Get event details
        event = input("Enter the event type: ")
        num_outfits = int(input("Number of outfits to generate: "))
        variations = int(input("Number of variations per outfit: "))
        
        # Generate outfits
        outfits = self.outfit_generator.generate_outfit(
            event=event,
            num_outfits=num_outfits,
            variations_per_outfit=variations,
            user_name=self.current_user
        )
        
        # Display generated outfits
        print("\nGenerated Outfits:")
        for i, outfit in enumerate(outfits, 1):
            print(f"\nOutfit {i}:")
            print(f"Top: {outfit['top']}")
            print(f"Bottom: {outfit['bottom']}")
            print(f"Shoes: {outfit['shoes']}")
            if outfit.get('extras'):
                print(f"Extras: {outfit['extras']}")
            
            # Save outfit to user's history first
            self.user_profile.add_outfit_to_history(self.current_user, outfit)
            
            # Ask for rating
            rate = input("\nWould you like to rate this outfit? (y/n): ").lower()
            if rate == 'y':
                self.rate_outfit(outfit)
            
            # Generate and save outfit image
            image_paths = self.outfit_generator.generate_outfit_image(outfit)
            if image_paths:
                self.user_profile.save_outfit_image(
                    self.current_user,
                    outfit.get('outfit_id', f'outfit_{i}'),
                    image_paths[0]
                )
    
    def view_style_history(self) -> None:
        """View user's style history."""
        if not self.current_user:
            print("Please login first.")
            return
        
        style_history = self.user_profile.get_style_history(self.current_user)
        if not style_history:
            print("No outfit history found.")
            return
        
        print("\n=== Your Style History ===")
        for outfit in style_history:
            print(f"\nEvent: {outfit['event']}")
            print(f"Created: {outfit['created_at']}")
            print(f"Top: {outfit['outfit_data']['top']}")
            print(f"Bottom: {outfit['outfit_data']['bottom']}")
            print(f"Shoes: {outfit['outfit_data']['shoes']}")
            if outfit['outfit_data'].get('extras'):
                print(f"Extras: {outfit['outfit_data']['extras']}")
    
    def run(self) -> None:
        """Run the main interface loop."""
        if not self.login():
            return
        
        while True:
            print("\n=== Fashion Outfit Generator ===")
            print("1. Generate Personalized Outfit")
            print("2. View Style History")
            print("3. Logout")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == "1":
                self.generate_personalized_outfit()
            elif choice == "2":
                self.view_style_history()
            elif choice == "3":
                self.current_user = None
                if not self.login():
                    break
            elif choice == "4":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    interface = UserInterface()
    interface.run() 