from typing import List, Optional, Dict, Any
import logging
import random
import json
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field
from material_specs import MaterialSpecifications

logger = logging.getLogger(__name__)

class UserProfile(BaseModel):
    """User profile with preferences and history."""
    user_id: str
    name: Optional[str] = None
    body_shape: Optional[str] = None  # pear, apple, rectangle, hourglass
    favorite_colors: List[str] = []
    preferred_materials: List[str] = []
    style_preferences: List[str] = []
    budget_range: Optional[Dict[str, float]] = None
    feedback_history: List[Dict] = []
    outfit_history: List[Dict] = []
    wishlist: List[Dict] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class OutfitFeedback(BaseModel):
    """Feedback for a generated outfit."""
    outfit_id: str
    user_id: str
    rating: int  # 1-5
    comments: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class OutfitHistory(BaseModel):
    """Historical record of generated outfits."""
    outfit_id: str
    user_id: str
    outfit_data: Dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.now)
    feedback: Optional[OutfitFeedback] = None
    is_favorite: bool = False

class WeatherContext(BaseModel):
    """Weather information for outfit generation."""
    temperature: float
    condition: str  # sunny, rainy, cloudy, etc.
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    location: str
    date: datetime = Field(default_factory=datetime.now)

class OutfitComponent(BaseModel):
    type: str
    color: str
    material: str
    fit: str
    style: str
    hem: Optional[str] = None
    bust_fit: Optional[str] = None
    shoulder_fit: Optional[str] = None
    arm_fit: Optional[str] = None
    waist_fit: Optional[str] = None
    hip_fit: Optional[str] = None
    length: Optional[str] = None
    surface_characteristics: List[str] = []
    draping: str = ""
    care_instructions: str = ""

class OutfitData(BaseModel):
    top: OutfitComponent
    bottom: OutfitComponent
    shoes: OutfitComponent
    extras: List[Dict]
    style: Dict[str, int]
    colors: List[str]
    materials: List[str]
    suitable_for: List[str]
    occasion: str
    season: str
    formality_level: int
    comfort_level: int
    # New richer fields
    complexity_level: Optional[str] = None
    estimated_hours: Optional[int] = None
    quality_control: Optional[List[str]] = []
    digital_rendering: Optional[Dict] = None
    design_notes: Optional[str] = None
    inspiration: Optional[str] = None
    material_costs: Optional[List[Dict]] = None
    sustainability_impact: Optional[Dict] = None

class DressMaker:
    def __init__(self):
        # Define style variations
        self.style_variations = {
            'casual': {
                'tops': [
                    {'description': 'White cotton t-shirt', 'material': 'cotton', 'color': 'white', 'fit': 'regular', 'features': ['crew neck', 'short sleeves']},
                    {'description': 'Striped button-up shirt', 'material': 'cotton', 'color': 'blue and white', 'fit': 'relaxed', 'features': ['button-up', 'long sleeves']},
                    {'description': 'Graphic print tank top', 'material': 'cotton blend', 'color': 'black', 'fit': 'slim', 'features': ['sleeveless', 'graphic print']}
                ],
                'bottoms': [
                    {'description': 'Blue jeans', 'material': 'denim', 'color': 'blue', 'fit': 'regular', 'features': ['five pocket', 'straight leg']},
                    {'description': 'Khaki chinos', 'material': 'cotton', 'color': 'khaki', 'fit': 'slim', 'features': ['flat front', 'tapered leg']},
                    {'description': 'Black joggers', 'material': 'cotton blend', 'color': 'black', 'fit': 'relaxed', 'features': ['elastic waist', 'cuffed ankles']}
                ],
                'shoes': [
                    # Low heel options
                    {'description': 'White sneakers', 'material': 'canvas', 'color': 'white', 'heel_height': 1, 'heel_width': 'wide', 'open_toe': False, 'comfort_level': 9},
                    {'description': 'Black slip-ons', 'material': 'canvas', 'color': 'black', 'heel_height': 1, 'heel_width': 'medium', 'open_toe': False, 'comfort_level': 8},
                    {'description': 'Brown leather loafers', 'material': 'leather', 'color': 'brown', 'heel_height': 1, 'heel_width': 'medium', 'open_toe': False, 'comfort_level': 8}
                ]
            },
            'formal': {
                'tops': [
                    {'description': 'White silk blouse', 'material': 'silk', 'color': 'white', 'fit': 'regular', 'features': ['ruffled collar', 'long sleeves']},
                    {'description': 'Black tailored shirt', 'material': 'cotton', 'color': 'black', 'fit': 'slim', 'features': ['button-up', 'long sleeves']},
                    {'description': 'Cream silk camisole', 'material': 'silk', 'color': 'cream', 'fit': 'slim', 'features': ['strappy', 'sleeveless']}
                ],
                'bottoms': [
                    {'description': 'Black pencil skirt', 'material': 'wool blend', 'color': 'black', 'fit': 'slim', 'features': ['knee length', 'back slit']},
                    {'description': 'Gray tailored pants', 'material': 'wool', 'color': 'gray', 'fit': 'slim', 'features': ['flat front', 'straight leg']},
                    {'description': 'Navy pleated skirt', 'material': 'wool blend', 'color': 'navy', 'fit': 'a-line', 'features': ['pleated', 'knee length']}
                ],
                'shoes': [
                    # Low heel options
                    {'description': 'Black leather flats', 'material': 'leather', 'color': 'black', 'heel_height': 1, 'heel_width': 'medium', 'open_toe': False, 'comfort_level': 8},
                    {'description': 'Nude leather pumps', 'material': 'leather', 'color': 'nude', 'heel_height': 2, 'heel_width': 'medium', 'open_toe': False, 'comfort_level': 7},
                    {'description': 'Black suede ankle boots', 'material': 'suede', 'color': 'black', 'heel_height': 4, 'heel_width': 'medium', 'open_toe': False, 'comfort_level': 7}
                ]
            }
        }

        # Add new data directories
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.profiles_dir = self.data_dir / "profiles"
        self.profiles_dir.mkdir(exist_ok=True)
        self.history_dir = self.data_dir / "history"
        self.history_dir.mkdir(exist_ok=True)
        
        # Load dynamic catalogs
        self.load_dynamic_catalogs()

    def load_dynamic_catalogs(self):
        """Load materials, colors, and styles from external files."""
        try:
            catalog_dir = self.data_dir / "catalogs"
            catalog_dir.mkdir(exist_ok=True)
            
            # Load materials catalog
            materials_file = catalog_dir / "materials.json"
            if materials_file.exists():
                with open(materials_file) as f:
                    self.materials_catalog = json.load(f)
            else:
                self.materials_catalog = {}
                
            # Load colors catalog
            colors_file = catalog_dir / "colors.json"
            if colors_file.exists():
                with open(colors_file) as f:
                    self.colors_catalog = json.load(f)
            else:
                self.colors_catalog = {}
                
            # Load styles catalog
            styles_file = catalog_dir / "styles.json"
            if styles_file.exists():
                with open(styles_file) as f:
                    self.styles_catalog = json.load(f)
            else:
                self.styles_catalog = {}
                
        except Exception as e:
            logger.error(f"Error loading dynamic catalogs: {e}")
            self.materials_catalog = {}
            self.colors_catalog = {}
            self.styles_catalog = {}

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve a user's profile."""
        profile_file = self.profiles_dir / f"{user_id}.json"
        if profile_file.exists():
            try:
                with open(profile_file) as f:
                    data = json.load(f)
                    return UserProfile(**data)
            except Exception as e:
                logger.error(f"Error loading user profile {user_id}: {e}")
        return None

    def save_user_profile(self, profile: UserProfile):
        """Save a user's profile."""
        try:
            profile_file = self.profiles_dir / f"{profile.user_id}.json"
            with open(profile_file, 'w') as f:
                json.dump(profile.dict(), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving user profile {profile.user_id}: {e}")

    def add_outfit_feedback(self, feedback: Dict):
        """Record feedback for an outfit."""
        try:
            # Convert dict to OutfitFeedback if needed
            if isinstance(feedback, dict):
                feedback = OutfitFeedback(**feedback)
            
            # Update user profile with feedback
            profile = self.get_user_profile(feedback.user_id)
            if profile:
                profile.feedback_history.append(feedback.model_dump())
                profile.updated_at = datetime.now()
                self.save_user_profile(profile)
            
            # Update outfit history
            history_file = self.history_dir / f"{feedback.outfit_id}.json"
            if history_file.exists():
                with open(history_file) as f:
                    history_data = json.load(f)
                history_data['feedback'] = feedback.model_dump()
                with open(history_file, 'w') as f:
                    json.dump(history_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving outfit feedback: {e}")

    def get_outfit_history(self, user_id: str) -> List[OutfitHistory]:
        """Retrieve a user's outfit history."""
        history = []
        try:
            for history_file in self.history_dir.glob("*.json"):
                with open(history_file) as f:
                    data = json.load(f)
                    if data.get('user_id') == user_id:
                        history.append(OutfitHistory(**data))
        except Exception as e:
            logger.error(f"Error loading outfit history for user {user_id}: {e}")
        return history

    def adjust_for_weather(self, outfit_data: OutfitData, weather: WeatherContext) -> OutfitData:
        """Adjust outfit based on weather conditions."""
        try:
            # Initialize design notes if None
            if outfit_data.design_notes is None:
                outfit_data.design_notes = ""
            
            # Adjust materials based on temperature
            if weather.temperature < 10:  # Cold
                outfit_data.materials = [m for m in outfit_data.materials if m in ['wool', 'cashmere', 'fleece']]
            elif weather.temperature > 25:  # Hot
                outfit_data.materials = [m for m in outfit_data.materials if m in ['cotton', 'linen', 'silk']]
            
            # Adjust for rain
            if weather.condition == 'rainy':
                outfit_data.extras.append({
                    'type': 'umbrella',
                    'description': 'Stylish umbrella',
                    'material': 'waterproof fabric',
                    'color': 'black',
                    'features': ['waterproof', 'windproof'],
                    'placement': 'hand',
                    'size': 'medium',
                    'style': outfit_data.style.get('formal', 5) > 5 and 'formal' or 'casual'
                })
            
            # Add weather note to design notes
            outfit_data.design_notes += f"\nWeather-adjusted for {weather.condition} conditions in {weather.location}"
            
        except Exception as e:
            logger.error(f"Error adjusting outfit for weather: {e}")
        
        return outfit_data

    def adjust_for_body_shape(self, outfit_data: OutfitData, body_shape: str) -> OutfitData:
        """Adjust outfit components to flatter the user's body shape."""
        try:
            # Initialize design notes if None
            if outfit_data.design_notes is None:
                outfit_data.design_notes = ""
            
            if body_shape == 'pear':
                # Emphasize shoulders, minimize hips
                outfit_data.top.style = 'structured'
                outfit_data.bottom.style = 'a-line'
            elif body_shape == 'apple':
                # Create waist definition, balance proportions
                outfit_data.top.style = 'fitted'
                outfit_data.bottom.style = 'straight'
            elif body_shape == 'rectangle':
                # Create curves, add definition
                outfit_data.top.style = 'fitted'
                outfit_data.bottom.style = 'a-line'
            elif body_shape == 'hourglass':
                # Maintain balance, emphasize waist
                outfit_data.top.style = 'fitted'
                outfit_data.bottom.style = 'fitted'
            
            outfit_data.design_notes += f"\nAdjusted for {body_shape} body shape"
            
        except Exception as e:
            logger.error(f"Error adjusting outfit for body shape: {e}")
        
        return outfit_data

    def _generate_outfit_data(self, event: str, outfit_number: int, variation: int,
                            is_character_outfit: bool, character_context: Optional[Dict],
                            real_world_context: Optional[Dict], style_expression: Optional[str],
                            user_name: Optional[str]) -> OutfitData:
        """Generate outfit data based on the given parameters."""
        # Determine style based on event type
        style = 'formal' if event in ['formal', 'business', 'wedding', 'gala'] else 'casual'
        logger.info(f"Generating {style} outfit for event: {event}")
        
        # Get user preferences from real_world_context if available
        user_profile = real_world_context.get('user_profile', {}) if real_world_context else {}
        if user_profile:
            logger.info(f"Using preferences for user: {user_profile.get('name', 'Unknown')}")

        # Initialize material specifications
        specs = MaterialSpecifications()
        
        # Get appropriate materials based on season and formality
        season = real_world_context.get('season', 'all') if real_world_context else 'all'
        formality = 'formal' if style == 'formal' else 'casual'
        allowed_outfit_materials = specs.recommend_materials(season, formality)
        logger.info(f"Allowed materials for {season} {formality} outfit: {allowed_outfit_materials}")

        # Restrict user material prefs to outfit materials
        outfit_material_prefs = [m for m in user_profile.get('preferred_materials', []) if m in allowed_outfit_materials]
        if outfit_material_prefs != user_profile.get('preferred_materials', []):
            logger.info(f"Filtered user's preferred materials from {user_profile.get('preferred_materials', [])} to {outfit_material_prefs} based on season and formality")
        user_profile['preferred_materials'] = outfit_material_prefs

        # Get random variations for each component
        top_data = random.choice(self.style_variations[style]['tops'])
        bottom_data = random.choice(self.style_variations[style]['bottoms'])
        shoes_data = random.choice(self.style_variations[style]['shoes'])
        
        logger.info(f"Selected base components - Top: {top_data['description']}, Bottom: {bottom_data['description']}, Shoes: {shoes_data['description']}")

        # Create OutfitComponent instances with material details
        top = OutfitComponent(
            type='top',
            color=top_data['color'],
            material=top_data['material'],
            fit=top_data.get('fit', 'comfortable'),
            style=style,
            hem=None,
            bust_fit='comfortable',
            shoulder_fit='perfect',
            arm_fit='relaxed',
            surface_characteristics=top_data.get('features', []),
            draping="",
            care_instructions="Dry clean only"
        )

        bottom = OutfitComponent(
            type='bottom',
            color=bottom_data['color'],
            material=bottom_data['material'],
            fit=bottom_data.get('fit', 'fitted'),
            style=style,
            waist_fit='fitted',
            hip_fit='comfortable',
            length='knee',
            surface_characteristics=bottom_data.get('features', []),
            draping="",
            care_instructions="Dry clean only"
        )

        shoes = OutfitComponent(
            type='shoes',
            color=shoes_data['color'],
            material=shoes_data['material'],
            fit=shoes_data.get('fit', 'comfortable'),
            style=style,
            surface_characteristics=shoes_data.get('features', []),
            draping="",
            care_instructions="Clean as directed"
        )

        # Add material details from specs
        for component in [top, bottom, shoes]:
            material_details = specs.get_material_properties(component.material)
            logger.info(f"Adding material details for {component.type} - Material: {component.material}, Properties: {material_details}")
            component.surface_characteristics.extend(material_details.get('surface_characteristics', []))
            component.draping = material_details.get('draping', '')
            component.care_instructions = material_details.get('care_instructions', '')

        # Enforce user color/material preferences
        if user_profile.get('favorite_colors'):
            if top.color not in user_profile['favorite_colors']:
                logger.info(f"Top color '{top.color}' not in user favorites {user_profile['favorite_colors']}. Replacing.")
                top.color = random.choice(user_profile['favorite_colors'])
                logger.info(f"Top color set to '{top.color}' based on user preference.")
            else:
                logger.info(f"Top color '{top.color}' matches user favorites.")
            if bottom.color not in user_profile['favorite_colors']:
                logger.info(f"Bottom color '{bottom.color}' not in user favorites {user_profile['favorite_colors']}. Replacing.")
                bottom.color = random.choice(user_profile['favorite_colors'])
                logger.info(f"Bottom color set to '{bottom.color}' based on user preference.")
            else:
                logger.info(f"Bottom color '{bottom.color}' matches user favorites.")

        if user_profile.get('preferred_materials'):
            if top.material not in user_profile['preferred_materials']:
                logger.info(f"Top material '{top.material}' not in user preferred materials {user_profile['preferred_materials']}. Replacing.")
                top.material = random.choice(user_profile['preferred_materials'])
                logger.info(f"Top material set to '{top.material}' based on user preference.")
            else:
                logger.info(f"Top material '{top.material}' matches user preferences.")
            if bottom.material not in user_profile['preferred_materials']:
                logger.info(f"Bottom material '{bottom.material}' not in user preferred materials {user_profile['preferred_materials']}. Replacing.")
                bottom.material = random.choice(user_profile['preferred_materials'])
                logger.info(f"Bottom material set to '{bottom.material}' based on user preference.")
            else:
                logger.info(f"Bottom material '{bottom.material}' matches user preferences.")

        # Handle coverage interplay
        interplay = user_profile.get('coverage_interplay')
        if interplay == 'cropped':
            top.hem = 'cropped at waist'
        elif interplay == 'flare':
            top.hem = 'flares 3 inches below waist'
        elif interplay == 'tucked':
            top.hem = 'tucked into bottom'

        # Add fit information
        top.bust_fit = 'comfortable'
        top.shoulder_fit = 'perfect'
        top.arm_fit = 'relaxed'
        
        bottom.waist_fit = 'fitted'
        bottom.hip_fit = 'comfortable'
        bottom.length = 'knee'

        # Generate accessories based on style
        extras = []
        if style == 'formal':
            extras = [
                {
                    'type': 'necklace',
                    'description': 'Pearl necklace',
                    'material': 'pearl',
                    'color': 'white',
                    'features': ['single strand'],
                    'placement': 'neck',
                    'size': 'medium',
                    'style': 'classic'
                }
            ]
        else:
            extras = [
                {
                    'type': 'bracelet',
                    'description': 'Leather bracelet',
                    'material': 'leather',
                    'color': 'brown',
                    'features': ['adjustable'],
                    'placement': 'wrist',
                    'size': 'one size',
                    'style': 'casual'
                }
            ]

        # Create the outfit data
        outfit_data = OutfitData(
            top=top,
            bottom=bottom,
            shoes=shoes,
            extras=extras,
            style={'formal': 8 if style == 'formal' else 3, 'classic': 7, 'elegant': 9 if style == 'formal' else 4},
            colors=[top.color, bottom.color, shoes.color],
            materials=[top.material, bottom.material, shoes.material],
            suitable_for=[event],
            occasion=event,
            season=season,
            formality_level=real_world_context.get('formality', 5) if real_world_context else 5,
            comfort_level=8,
            complexity_level=None,  # Will be calculated later
            estimated_hours=None,   # Will be calculated later
            quality_control=[],     # Will be added later
            digital_rendering=None, # Will be added later
            design_notes=None,      # Will be added later
            inspiration=None,       # Will be added later
            material_costs=None,    # Will be calculated later
            sustainability_impact=None  # Will be calculated later
        )

        return outfit_data

    def _generate_best_component(self, component: str, outfit_data: OutfitData, real_world_context: Optional[Dict]) -> Optional[Dict]:
        """Generate the best component based on user preferences and context."""
        style = 'formal' if outfit_data.formality_level >= 7 else 'casual'
        candidates = self.style_variations[style][f'{component}s']
        user_profile = real_world_context.get('user_profile', {}) if real_world_context else {}

        # Score candidates based on preferences
        def score(c):
            score = 0
            if user_profile.get('preferred_materials') and c['material'] in user_profile['preferred_materials']:
                score += 2
            if user_profile.get('favorite_colors') and c['color'] in user_profile['favorite_colors']:
                score += 2
            # Add style matching score
            if user_profile.get('style_preferences'):
                for pref in user_profile['style_preferences']:
                    if pref in c.get('features', []):
                        score += 1
            return score

        candidates = sorted(candidates, key=score, reverse=True)
        if not candidates:
            return None
            
        # Create OutfitComponent with proper type field
        best_candidate = candidates[0]
        return OutfitComponent(
            type=component,  # Use the component name as type
            color=best_candidate['color'],
            material=best_candidate['material'],
            fit=best_candidate.get('fit', 'regular'),
            style=style,
            surface_characteristics=best_candidate.get('features', []),
            care_instructions="Follow care label instructions"
        )

    def _calculate_complexity(self, outfit_data: OutfitData) -> str:
        """Estimate complexity level based on materials and style."""
        complexity_score = 0
        
        # Base complexity from formality
        if outfit_data.formality_level >= 7:
            complexity_score += 3
        elif outfit_data.formality_level >= 5:
            complexity_score += 2
        else:
            complexity_score += 1
            
        # Add complexity for number of materials
        complexity_score += min(len(set(outfit_data.materials)), 3)
        
        # Add complexity for special features
        for component in [outfit_data.top, outfit_data.bottom, outfit_data.shoes]:
            if component.surface_characteristics:
                complexity_score += len(component.surface_characteristics) // 2
                
        # Convert score to level
        if complexity_score >= 6:
            return "very high"
        elif complexity_score >= 4:
            return "high"
        elif complexity_score >= 2:
            return "medium"
        else:
            return "low"

    def _estimate_hours(self, outfit_data: OutfitData) -> int:
        """Estimate hours based on complexity and components."""
        base_hours = {
            "very high": 160,
            "high": 120,
            "medium": 80,
            "low": 40
        }
        
        hours = base_hours.get(outfit_data.complexity_level, 80)
        
        # Add hours for special features
        for component in [outfit_data.top, outfit_data.bottom, outfit_data.shoes]:
            if component.surface_characteristics:
                hours += len(component.surface_characteristics) * 5
                
        return hours

    def _calculate_material_costs(self, outfit_data: OutfitData) -> List[Dict]:
        """Calculate material costs based on components and complexity."""
        costs = []
        base_costs = {
            "silk": 1000.0,
            "cotton": 500.0,
            "wool": 800.0,
            "leather": 1200.0,
            "denim": 600.0
        }
        
        for material in set(outfit_data.materials):
            base_cost = base_costs.get(material, 500.0)
            quality_multiplier = 1.5 if outfit_data.formality_level >= 7 else 1.2
            complexity_multiplier = 1.3 if outfit_data.complexity_level in ["high", "very high"] else 1.1
            
            costs.append({
                "fabric_type": material,
                "base_cost": base_cost,
                "quality_multiplier": quality_multiplier,
                "complexity_multiplier": complexity_multiplier,
                "total_cost": base_cost * quality_multiplier * complexity_multiplier
            })
            
        return costs

    def _get_sustainability_impact(self, outfit_data: OutfitData) -> Dict:
        """Calculate sustainability impact based on materials and construction."""
        sustainable_materials = ["organic cotton", "recycled polyester", "hemp", "bamboo"]
        certifications = []
        
        for material in outfit_data.materials:
            if material.lower() in sustainable_materials:
                certifications.append(f"{material.upper()}_CERTIFIED")
                
        return {
            "materials": [m for m in outfit_data.materials if m.lower() in sustainable_materials],
            "certifications": certifications
        }

    def _handle_allergies(self, outfit_data: OutfitData, allergies: List[str]) -> OutfitData:
        """Handle material allergies in outfit generation."""
        if not allergies:
            return outfit_data
            
        logger.info(f"Checking for allergies: {allergies}")
        for component in [outfit_data.top, outfit_data.bottom, outfit_data.shoes]:
            if component.material.lower() in [a.lower() for a in allergies]:
                logger.warning(f"Material {component.material} conflicts with allergies {allergies}")
                # Find alternative material
                alternative_materials = [m for m in self.materials_catalog.keys() 
                                      if m.lower() not in [a.lower() for a in allergies]]
                if alternative_materials:
                    old_material = component.material
                    component.material = random.choice(alternative_materials)
                    logger.info(f"Replaced {old_material} with {component.material} due to allergies")
                else:
                    logger.error("No suitable alternative materials found for allergies")
        
        return outfit_data

    def _handle_safety_requirements(self, outfit_data: OutfitData, requirements: List[str]) -> OutfitData:
        """Handle safety requirements in outfit generation."""
        if not requirements:
            return outfit_data
            
        logger.info(f"Applying safety requirements: {requirements}")
        
        # Handle waterproof requirement
        if "waterproof" in requirements:
            logger.info("Adding waterproof materials and features")
            for component in [outfit_data.top, outfit_data.bottom]:
                if component.material not in ["goretex", "nylon", "polyester"]:
                    component.material = random.choice(["goretex", "nylon", "polyester"])
                component.surface_characteristics.append("waterproof")
            
            # Add waterproof outer layer
            outfit_data.extras.append({
                'type': 'outerwear',
                'description': 'Waterproof jacket',
                'material': 'goretex',
                'color': 'black',
                'features': ['waterproof', 'windproof', 'hooded'],
                'placement': 'outer',
                'size': 'regular',
                'style': 'functional'
            })
        
        # Handle high visibility requirement
        if "high_visibility" in requirements:
            logger.info("Adding high visibility features")
            for component in [outfit_data.top, outfit_data.bottom]:
                if component.color not in ["neon yellow", "neon orange", "neon green"]:
                    component.color = random.choice(["neon yellow", "neon orange", "neon green"])
                component.surface_characteristics.append("reflective")
            
            # Add reflective accessories
            outfit_data.extras.append({
                'type': 'accessory',
                'description': 'Reflective vest',
                'material': 'reflective fabric',
                'color': 'neon yellow',
                'features': ['reflective', 'high visibility'],
                'placement': 'outer',
                'size': 'regular',
                'style': 'safety'
            })
        
        return outfit_data

    def generate_outfit(self, event: str, num_outfits: int, variations_per_outfit: int,
                       is_character_outfit: bool = False,
                       character_context: Optional[Dict] = None,
                       real_world_context: Optional[Dict] = None,
                       style_expression: Optional[str] = None,
                       user_name: Optional[str] = None,
                       max_retries: int = 3) -> List[OutfitData]:
        """Enhanced outfit generation with user context and weather awareness."""
        outfits = []
        
        # Get user profile if available
        user_profile = None
        if real_world_context and 'user_id' in real_world_context:
            user_profile = self.get_user_profile(real_world_context['user_id'])
        
        # Get weather context if available
        weather_context = None
        if real_world_context and 'weather' in real_world_context:
            weather_context = WeatherContext(**real_world_context['weather'])
        
        for outfit_number in range(1, num_outfits + 1):
            for variation in range(1, variations_per_outfit + 1):
                retries = 0
                while retries < max_retries:
                    try:
                        # Generate base outfit
                        outfit_data = self._generate_outfit_data(
                            event, outfit_number, variation,
                            is_character_outfit, character_context,
                            real_world_context, style_expression,
                            user_name
                        )
                        
                        # Apply user profile adjustments
                        if user_profile:
                            outfit_data = self.adjust_for_body_shape(outfit_data, user_profile.body_shape)
                        
                        # Apply weather adjustments
                        if weather_context:
                            outfit_data = self.adjust_for_weather(outfit_data, weather_context)
                        
                        # Handle allergies if specified
                        if real_world_context and 'allergies' in real_world_context:
                            outfit_data = self._handle_allergies(outfit_data, real_world_context['allergies'])
                        
                        # Handle safety requirements if specified
                        if real_world_context and 'safety_requirements' in real_world_context:
                            outfit_data = self._handle_safety_requirements(outfit_data, real_world_context['safety_requirements'])
                        
                        # Add richer data
                        outfit_data.complexity_level = self._calculate_complexity(outfit_data)
                        outfit_data.estimated_hours = self._estimate_hours(outfit_data)
                        outfit_data.quality_control = [
                            "Precise pattern matching",
                            "Perfect seam alignment",
                            "Impeccable hand-finishing",
                            "Fabric grain alignment",
                            "Drape verification",
                            "Fit assessment"
                        ]
                        outfit_data.digital_rendering = {
                            "available_views": ["front", "back", "side", "detail"],
                            "material_swatches": []
                        }
                        outfit_data.design_notes = f"Generated for {event} with {user_name if user_name else 'default'} preferences"
                        outfit_data.inspiration = f"Outfit variation {variation} for {event}"
                        outfit_data.material_costs = self._calculate_material_costs(outfit_data)
                        outfit_data.sustainability_impact = self._get_sustainability_impact(outfit_data)
                        
                        # Validate with Pydantic
                        try:
                            outfit_data = OutfitData.model_validate(outfit_data)
                        except Exception as e:
                            logger.error(f"Pydantic validation failed: {e}")
                            retries += 1
                            continue
                        
                        # Handle missing components
                        missing_components = self._get_missing_components(outfit_data)
                        if missing_components:
                            for component in missing_components:
                                generated_component = self._generate_best_component(component, outfit_data, real_world_context)
                                if generated_component:
                                    setattr(outfit_data, component, generated_component)
                                else:
                                    break
                        
                        # Final validation
                        if self._validate_outfit_data(outfit_data):
                            # Save to history if user profile exists
                            if user_profile:
                                outfit_id = f"{event}_{outfit_number}_{variation}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                                history = OutfitHistory(
                                    outfit_id=outfit_id,
                                    user_id=user_profile.user_id,
                                    outfit_data=outfit_data.dict()
                                )
                                history_file = self.history_dir / f"{outfit_id}.json"
                                with open(history_file, 'w') as f:
                                    json.dump(history.dict(), f, indent=2, default=str)
                            
                            outfits.append(outfit_data)
                            break
                        else:
                            retries += 1
                            
                    except Exception as e:
                        logger.error(f"Error generating outfit: {str(e)}")
                        retries += 1
                
                if retries == max_retries:
                    logger.error(f"Failed to generate valid outfit after {max_retries} attempts")
        
        return outfits

    def _get_missing_components(self, outfit_data: OutfitData) -> List[str]:
        """Check for missing required components in the outfit data."""
        required_components = ['top', 'bottom', 'shoes']
        missing = []
        for comp in required_components:
            try:
                getattr(outfit_data, comp)
            except AttributeError:
                missing.append(comp)
        return missing

    def _validate_outfit_data(self, outfit_data: OutfitData) -> bool:
        """Validate the outfit data."""
        try:
            # Check required components
            if not all(hasattr(outfit_data, comp) for comp in ['top', 'bottom', 'shoes']):
                logger.error("Missing required components")
                return False

            # Validate component types
            if not isinstance(outfit_data.top, OutfitComponent):
                logger.error("Invalid top component type")
                return False
            if not isinstance(outfit_data.bottom, OutfitComponent):
                logger.error("Invalid bottom component type")
                return False
            if not isinstance(outfit_data.shoes, OutfitComponent):
                logger.error("Invalid shoes component type")
                return False

            # Validate component fields
            for component_name in ['top', 'bottom', 'shoes']:
                component = getattr(outfit_data, component_name)
                if not all(hasattr(component, field) for field in ['type', 'color', 'material', 'fit', 'style']):
                    logger.error(f"Missing required fields in {component_name}")
                    return False

            # Validate lists and dicts
            if not isinstance(outfit_data.extras, list):
                logger.error("Invalid extras type")
                return False
            if not isinstance(outfit_data.style, dict):
                logger.error("Invalid style type")
                return False
            if not isinstance(outfit_data.colors, list):
                logger.error("Invalid colors type")
                return False
            if not isinstance(outfit_data.materials, list):
                logger.error("Invalid materials type")
                return False
            if not isinstance(outfit_data.suitable_for, list):
                logger.error("Invalid suitable_for type")
                return False

            # Validate required fields
            required_fields = [
                'occasion', 'season', 'formality_level', 'comfort_level',
                'complexity_level', 'estimated_hours', 'quality_control',
                'digital_rendering', 'design_notes', 'inspiration',
                'material_costs', 'sustainability_impact'
            ]
            if not all(hasattr(outfit_data, field) for field in required_fields):
                logger.error("Missing required fields in outfit data")
                return False

            logger.info("All validations passed")
            return True

        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False