"""
User Profile and Preferences Management for Fashion Outfit Generator.
Handles user measurements, style preferences, and personalization settings.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Union
from enum import Enum
import json
import logging
import os
import hashlib
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class MeasurementUnit(Enum):
    """Supported measurement units."""
    INCHES = "inches"
    CM = "cm"
    LBS = "lbs"
    KG = "kg"
    STONE = "stone"

class CupSize(Enum):
    """American cup sizes."""
    AA = "AA"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    DD = "DD"
    DDD = "DDD"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"
    J = "J"
    K = "K"

@dataclass
class BustMeasurement:
    """Bust measurement with band size and cup size."""
    band_size: float
    cup_size: CupSize
    unit: MeasurementUnit = MeasurementUnit.INCHES

    def __str__(self) -> str:
        return f"{self.band_size}{self.cup_size.value}"

    def to_dict(self) -> Dict:
        return {
            'band_size': self.band_size,
            'cup_size': self.cup_size.value,
            'unit': self.unit.value
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'BustMeasurement':
        return cls(
            band_size=data['band_size'],
            cup_size=CupSize(data['cup_size']),
            unit=MeasurementUnit(data['unit'])
        )

@dataclass
class Measurements:
    """User measurements with type-safe units."""
    height: float
    height_unit: MeasurementUnit
    weight: float
    weight_unit: MeasurementUnit
    bust: Optional[Union[float, BustMeasurement]] = None
    waist: Optional[float] = None
    hips: Optional[float] = None
    inseam: Optional[float] = None
    shoulder_width: Optional[float] = None
    arm_length: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert measurements to dictionary format."""
        data = {
            'height': self.height,
            'height_unit': self.height_unit.value,
            'weight': self.weight,
            'weight_unit': self.weight_unit.value,
            'waist': self.waist,
            'hips': self.hips,
            'inseam': self.inseam,
            'shoulder_width': self.shoulder_width,
            'arm_length': self.arm_length
        }
        
        if self.bust is not None:
            if isinstance(self.bust, BustMeasurement):
                data['bust'] = self.bust.to_dict()
            else:
                data['bust'] = self.bust
        
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Measurements':
        """Create Measurements instance from dictionary."""
        bust = data.get('bust')
        if bust and isinstance(bust, dict):
            bust = BustMeasurement.from_dict(bust)
        
        return cls(
            height=data['height'],
            height_unit=MeasurementUnit(data['height_unit']),
            weight=data['weight'],
            weight_unit=MeasurementUnit(data['weight_unit']),
            bust=bust,
            waist=data.get('waist'),
            hips=data.get('hips'),
            inseam=data.get('inseam'),
            shoulder_width=data.get('shoulder_width'),
            arm_length=data.get('arm_length')
        )

class StylePreference(Enum):
    """Style preference categories."""
    CLASSIC = "classic"
    MODERN = "modern"
    BOHEMIAN = "bohemian"
    MINIMALIST = "minimalist"
    EDGY = "edgy"
    ROMANTIC = "romantic"
    SPORTY = "sporty"
    LUXURY = "luxury"
    CASUAL = "casual"
    FORMAL = "formal"

@dataclass
class PhysicalFeatures:
    """User's physical features."""
    eye_color: str
    hair_color: str
    hair_length: str
    skin_tone: str
    body_type: str
    face_shape: Optional[str] = None
    distinguishing_features: Optional[List[str]] = None

@dataclass
class StylePreferences:
    """User's style preferences and comfort levels."""
    primary_style: StylePreference
    secondary_styles: Set[StylePreference]
    favorite_colors: Set[str]
    favorite_materials: Set[str]
    preferred_silhouettes: Set[str]
    style_adaptability: int  # 1-10 scale
    comfort_priority: int  # 1-10 scale
    modesty_level: int  # 1-10 scale
    color_preferences: Dict[str, int]  # Color: preference score (1-10)
    material_preferences: Dict[str, int]  # Material: preference score (1-10)
    style_restrictions: Optional[List[str]] = None
    seasonal_preferences: Optional[Dict[str, int]] = None

class UserProfile:
    """Manages user profiles and preferences."""
    
    def __init__(self):
        self.profiles: Dict[str, 'UserProfile'] = {}
        self.current_user: Optional[str] = None
        self.base_dir = Path("user_data")
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure necessary directories exist."""
        self.base_dir.mkdir(exist_ok=True)
        (self.base_dir / "profiles").mkdir(exist_ok=True)
        (self.base_dir / "outfits").mkdir(exist_ok=True)
        (self.base_dir / "images").mkdir(exist_ok=True)
        (self.base_dir / "style_history").mkdir(exist_ok=True)
    
    def _get_user_dir(self, name: str) -> Path:
        """Get user-specific directory."""
        user_hash = hashlib.md5(name.lower().encode()).hexdigest()
        user_dir = self.base_dir / user_hash
        user_dir.mkdir(exist_ok=True)
        (user_dir / "outfits").mkdir(exist_ok=True)
        (user_dir / "images").mkdir(exist_ok=True)
        (user_dir / "style_history").mkdir(exist_ok=True)
        return user_dir
    
    def is_new_user(self, name: str) -> bool:
        """Check if user is new."""
        profile_path = self.base_dir / "profiles" / f"{name.lower()}.json"
        return not profile_path.exists()
    
    def create_profile(self, name: str, measurements: Measurements, 
                      physical_features: PhysicalFeatures,
                      style_preferences: StylePreferences) -> None:
        """Create a new user profile."""
        try:
            profile = {
                'name': name,
                'measurements': measurements.to_dict(),
                'physical_features': physical_features.__dict__,
                'style_preferences': {
                    'primary_style': style_preferences.primary_style.value,
                    'secondary_styles': [style.value for style in style_preferences.secondary_styles],
                    'favorite_colors': list(style_preferences.favorite_colors),
                    'favorite_materials': list(style_preferences.favorite_materials),
                    'preferred_silhouettes': list(style_preferences.preferred_silhouettes),
                    'style_adaptability': style_preferences.style_adaptability,
                    'comfort_priority': style_preferences.comfort_priority,
                    'modesty_level': style_preferences.modesty_level,
                    'color_preferences': style_preferences.color_preferences,
                    'material_preferences': style_preferences.material_preferences,
                    'style_restrictions': style_preferences.style_restrictions,
                    'seasonal_preferences': style_preferences.seasonal_preferences
                },
                'created_at': datetime.now().isoformat(),
                'last_login': datetime.now().isoformat(),
                'outfit_count': 0,
                'style_history': []
            }
            
            # Save profile to file
            profile_path = self.base_dir / "profiles" / f"{name.lower()}.json"
            with open(profile_path, 'w') as f:
                json.dump(profile, f, indent=2)
            
            self.profiles[name] = profile
            logger.info(f"Created profile for user: {name}")
        except Exception as e:
            logger.error(f"Error creating profile: {str(e)}")
            raise
    
    def get_profile(self, name: str) -> Optional[Dict]:
        """Get a user's profile."""
        return self.profiles.get(name)
    
    def update_measurements(self, name: str, measurements: Measurements) -> None:
        """Update a user's measurements."""
        if name in self.profiles:
            self.profiles[name]['measurements'] = measurements.to_dict()
            logger.info(f"Updated measurements for user: {name}")
    
    def update_style_preferences(self, name: str, 
                               style_preferences: StylePreferences) -> None:
        """Update a user's style preferences."""
        if name in self.profiles:
            self.profiles[name]['style_preferences'] = {
                'primary_style': style_preferences.primary_style.value,
                'secondary_styles': [style.value for style in style_preferences.secondary_styles],
                'favorite_colors': list(style_preferences.favorite_colors),
                'favorite_materials': list(style_preferences.favorite_materials),
                'preferred_silhouettes': list(style_preferences.preferred_silhouettes),
                'style_adaptability': style_preferences.style_adaptability,
                'comfort_priority': style_preferences.comfort_priority,
                'modesty_level': style_preferences.modesty_level,
                'color_preferences': style_preferences.color_preferences,
                'material_preferences': style_preferences.material_preferences,
                'style_restrictions': style_preferences.style_restrictions,
                'seasonal_preferences': style_preferences.seasonal_preferences
            }
            logger.info(f"Updated style preferences for user: {name}")
    
    def get_style_guidance(self, name: str) -> Dict:
        """Get style guidance based on user preferences."""
        profile = self.get_profile(name)
        if not profile:
            return {}
        
        style_prefs = profile['style_preferences']
        return {
            'primary_style': style_prefs['primary_style'],
            'secondary_styles': style_prefs['secondary_styles'],
            'favorite_colors': style_prefs['favorite_colors'],
            'favorite_materials': style_prefs['favorite_materials'],
            'preferred_silhouettes': style_prefs['preferred_silhouettes'],
            'style_adaptability': style_prefs['style_adaptability'],
            'comfort_priority': style_prefs['comfort_priority'],
            'modesty_level': style_prefs['modesty_level'],
            'color_preferences': style_prefs['color_preferences'],
            'material_preferences': style_prefs['material_preferences'],
            'style_restrictions': style_prefs['style_restrictions'],
            'seasonal_preferences': style_prefs['seasonal_preferences']
        }
    
    def get_measurement_guidance(self, name: str) -> Dict:
        """Get measurement guidance for outfit generation."""
        profile = self.get_profile(name)
        if not profile:
            return {}
        
        measurements = profile['measurements']
        return {
            'height': {
                'value': measurements['height'],
                'unit': measurements['height_unit']
            },
            'weight': {
                'value': measurements['weight'],
                'unit': measurements['weight_unit']
            },
            'bust': measurements['bust'],
            'waist': measurements['waist'],
            'hips': measurements['hips'],
            'inseam': measurements['inseam'],
            'shoulder_width': measurements['shoulder_width'],
            'arm_length': measurements['arm_length']
        }
    
    def get_physical_feature_guidance(self, name: str) -> Dict:
        """Get physical feature guidance for outfit generation."""
        profile = self.get_profile(name)
        if not profile:
            return {}
        
        features = profile['physical_features']
        return {
            'eye_color': features['eye_color'],
            'hair_color': features['hair_color'],
            'hair_length': features['hair_length'],
            'skin_tone': features['skin_tone'],
            'body_type': features['body_type'],
            'face_shape': features['face_shape'],
            'distinguishing_features': features['distinguishing_features']
        }
    
    def save_profile(self, name: str) -> bool:
        """Save a user profile to a JSON file."""
        try:
            profile = self.profiles.get(name)
            if not profile:
                logger.error(f"No profile found for user: {name}")
                return False
            
            # Ensure all required fields are present
            required_fields = ['name', 'measurements', 'physical_features', 'style_preferences', 
                             'created_at', 'last_login', 'outfit_count', 'style_history']
            for field in required_fields:
                if field not in profile:
                    logger.error(f"Missing required field in profile: {field}")
                    return False
            
            # Convert any sets to lists before saving
            if 'style_history' in profile:
                for outfit in profile['style_history']:
                    if 'outfit_data' in outfit:
                        for key in ['colors', 'materials', 'lengths', 'textures', 'styles']:
                            if key in outfit['outfit_data'] and isinstance(outfit['outfit_data'][key], set):
                                outfit['outfit_data'][key] = list(outfit['outfit_data'][key])
            
            # Convert any sets in style_preferences
            if 'style_preferences' in profile:
                for key in ['secondary_styles', 'favorite_colors', 'favorite_materials', 'preferred_silhouettes']:
                    if key in profile['style_preferences'] and isinstance(profile['style_preferences'][key], set):
                        profile['style_preferences'][key] = list(profile['style_preferences'][key])
            
            # Save to profiles directory
            profile_path = self.base_dir / "profiles" / f"{name.lower()}.json"
            with open(profile_path, 'w') as f:
                json.dump(profile, f, indent=2)
            logger.info(f"Profile saved for user: {name}")
            return True
        except Exception as e:
            logger.error(f"Error saving profile: {str(e)}")
            return False
    
    def load_profile(self, name: str) -> Optional[Dict]:
        """Load a user profile from a JSON file."""
        try:
            # Load from profiles directory
            profile_path = self.base_dir / "profiles" / f"{name.lower()}.json"
            if not profile_path.exists():
                logger.info(f"No profile found for user: {name}")
                return None
            
            with open(profile_path, 'r') as f:
                content = f.read()
            
            # Clean up the content
            content = content.replace('\n', ' ').replace('\r', '')
            content = content.replace('**', '')  # Remove markdown formatting
            content = content.replace('  ', ' ')  # Remove extra spaces
            
            try:
                profile = json.loads(content)
            except json.JSONDecodeError:
                # Try to fix common JSON issues
                content = content.replace("'", '"')  # Replace single quotes with double quotes
                content = content.replace("True", "true")  # Fix boolean values
                content = content.replace("False", "false")
                content = content.replace("None", "null")
                profile = json.loads(content)
            
            # Validate required fields
            required_fields = ['name', 'measurements', 'physical_features', 'style_preferences', 
                             'created_at', 'last_login', 'outfit_count', 'style_history']
            for field in required_fields:
                if field not in profile:
                    logger.error(f"Missing required field in profile: {field}")
                    return None
            
            # Convert lists back to sets where appropriate
            if 'style_history' in profile:
                for outfit in profile['style_history']:
                    if 'outfit_data' in outfit:
                        for key in ['colors', 'materials', 'lengths', 'textures', 'styles']:
                            if key in outfit['outfit_data'] and isinstance(outfit['outfit_data'][key], list):
                                outfit['outfit_data'][key] = set(outfit['outfit_data'][key])
            
            # Convert lists back to sets in style_preferences
            if 'style_preferences' in profile:
                for key in ['secondary_styles', 'favorite_colors', 'favorite_materials', 'preferred_silhouettes']:
                    if key in profile['style_preferences'] and isinstance(profile['style_preferences'][key], list):
                        profile['style_preferences'][key] = set(profile['style_preferences'][key])
            
            # Store in memory
            self.profiles[name] = profile
            logger.info(f"Profile loaded for user: {name}")
            return profile
        except Exception as e:
            logger.error(f"Error loading profile: {str(e)}")
            return None
    
    def add_outfit_to_history(self, name: str, outfit_data: Dict) -> None:
        """Add an outfit to user's style history."""
        try:
            profile = self.get_profile(name)
            if not profile:
                logger.error(f"No profile found for user: {name}")
                return
            
            # Clean up outfit data
            for key in ['top', 'bottom', 'shoes', 'extras']:
                if key in outfit_data and isinstance(outfit_data[key], str):
                    outfit_data[key] = outfit_data[key].replace('**', '').strip()
            
            outfit_entry = {
                'outfit_id': outfit_data.get('outfit_id', ''),
                'event': outfit_data.get('event', ''),
                'created_at': datetime.now().isoformat(),
                'outfit_data': outfit_data
            }
            
            profile['style_history'].append(outfit_entry)
            profile['outfit_count'] += 1
            self.save_profile(name)
            
            # Save outfit data to user's directory
            user_dir = self._get_user_dir(name)
            outfit_path = user_dir / "outfits" / f"{outfit_entry['outfit_id']}.json"
            with open(outfit_path, 'w') as f:
                json.dump(outfit_entry, f, indent=2)
        except Exception as e:
            logger.error(f"Error adding outfit to history: {str(e)}")
    
    def save_outfit_image(self, name: str, outfit_id: str, image_path: str) -> None:
        """Save an outfit image to user's directory."""
        user_dir = self._get_user_dir(name)
        image_dir = user_dir / "images"
        image_dir.mkdir(exist_ok=True)
        
        # Copy image to user's directory
        import shutil
        dest_path = image_dir / f"{outfit_id}.png"
        shutil.copy2(image_path, dest_path)
    
    def get_style_history(self, name: str) -> List[Dict]:
        """Get user's style history."""
        profile = self.get_profile(name)
        if profile:
            return profile.get('style_history', [])
        return []
    
    def get_outfit_count(self, name: str) -> int:
        """Get number of outfits generated for user."""
        profile = self.get_profile(name)
        if profile:
            return profile.get('outfit_count', 0)
        return 0
    
    def get_user_directory(self, name: str) -> Path:
        """Get user's directory path."""
        return self._get_user_dir(name)
    
    def set_current_user(self, name: str) -> None:
        """Set the current active user."""
        if name in self.profiles:
            self.current_user = name
            logger.info(f"Set current user to: {name}")
        else:
            logger.error(f"User not found: {name}")
    
    def get_current_user(self) -> Optional[str]:
        """Get the current active user."""
        return self.current_user
    
    def update_outfit_rating(self, name: str, outfit_id: str, ratings: Dict) -> None:
        """Update the rating for a specific outfit in user's history."""
        try:
            profile = self.get_profile(name)
            if not profile:
                logger.error(f"No profile found for user: {name}")
                return
            
            # Find the outfit in history
            for outfit in profile['style_history']:
                if outfit['outfit_id'] == outfit_id:
                    # Update the outfit data with new ratings
                    outfit['outfit_data']['user_ratings'] = ratings
                    self.save_profile(name)
                    
                    # Update the outfit file
                    user_dir = self._get_user_dir(name)
                    outfit_path = user_dir / "outfits" / f"{outfit_id}.json"
                    with open(outfit_path, 'w') as f:
                        json.dump(outfit, f, indent=2)
                    return
            
            logger.error(f"Outfit {outfit_id} not found in user's history")
        except Exception as e:
            logger.error(f"Error updating outfit rating: {str(e)}") 