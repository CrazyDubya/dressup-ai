from typing import List, Optional, Dict
import logging
import random
from pydantic import BaseModel

logger = logging.getLogger(__name__)

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
                    {'description': 'Brown leather loafers', 'material': 'leather', 'color': 'brown', 'heel_height': 1, 'heel_width': 'medium', 'open_toe': False, 'comfort_level': 8},
                    # Medium heel options
                    {'description': 'Black leather sandals', 'material': 'leather', 'color': 'black', 'heel_height': 5, 'heel_width': 'narrow', 'open_toe': True, 'comfort_level': 7},
                    {'description': 'White platform sandals', 'material': 'synthetic', 'color': 'white', 'heel_height': 6, 'heel_width': 'medium', 'open_toe': True, 'comfort_level': 6},
                    {'description': 'Brown leather mules', 'material': 'leather', 'color': 'brown', 'heel_height': 4, 'heel_width': 'narrow', 'open_toe': True, 'comfort_level': 7},
                    # High heel options
                    {'description': 'Black strappy sandals', 'material': 'leather', 'color': 'black', 'heel_height': 7, 'heel_width': 'narrow', 'open_toe': True, 'comfort_level': 5},
                    {'description': 'White wedge sandals', 'material': 'synthetic', 'color': 'white', 'heel_height': 8, 'heel_width': 'wide', 'open_toe': True, 'comfort_level': 6},
                    {'description': 'Brown leather ankle boots', 'material': 'leather', 'color': 'brown', 'heel_height': 7, 'heel_width': 'medium', 'open_toe': False, 'comfort_level': 6}
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
                    # Medium heel options
                    {'description': 'Black leather pumps', 'material': 'leather', 'color': 'black', 'heel_height': 5, 'heel_width': 'narrow', 'open_toe': False, 'comfort_level': 6},
                    {'description': 'Nude patent heels', 'material': 'patent leather', 'color': 'nude', 'heel_height': 6, 'heel_width': 'narrow', 'open_toe': False, 'comfort_level': 5},
                    {'description': 'Black suede ankle boots', 'material': 'suede', 'color': 'black', 'heel_height': 4, 'heel_width': 'medium', 'open_toe': False, 'comfort_level': 7},
                    # High heel options
                    {'description': 'Black stiletto pumps', 'material': 'leather', 'color': 'black', 'heel_height': 7, 'heel_width': 'narrow', 'open_toe': False, 'comfort_level': 4},
                    {'description': 'Nude strappy heels', 'material': 'leather', 'color': 'nude', 'heel_height': 8, 'heel_width': 'narrow', 'open_toe': True, 'comfort_level': 5},
                    {'description': 'Black platform pumps', 'material': 'leather', 'color': 'black', 'heel_height': 7, 'heel_width': 'medium', 'open_toe': False, 'comfort_level': 6}
                ]
            }
        }

    def _generate_outfit_data(self, event: str, outfit_number: int, variation: int,
                            is_character_outfit: bool, character_context: Optional[Dict],
                            real_world_context: Optional[Dict], style_expression: Optional[str],
                            user_name: Optional[str]) -> OutfitData:
        """Generate outfit data based on the given parameters."""
        # Determine style based on event type
        style = 'formal' if event in ['formal', 'business', 'wedding'] else 'casual'
        
        # Get user preferences from real_world_context if available
        user_profile = real_world_context.get('user_profile', {}) if real_world_context else {}

        # Normalize list preferences
        user_profile.setdefault('favorite_colors', [])
        user_profile.setdefault('preferred_materials', [])
        # Normalize bottom and coverage preferences
        user_profile.setdefault('bottom_preference', {})
        user_profile.setdefault('coverage_interplay', None)

        # Define allowed materials for components
        allowed_outfit_materials = {'cotton', 'silk', 'wool', 'denim', 'linen'}
        allowed_shoe_materials = {s['material'] for s in self.style_variations[style]['shoes']}

        # Restrict user material prefs to outfit materials
        outfit_material_prefs = [m for m in user_profile['preferred_materials'] if m in allowed_outfit_materials]
        user_profile['preferred_materials'] = outfit_material_prefs

        # Get random variations for each component
        top_data = random.choice(self.style_variations[style]['tops'])
        bottom_data = random.choice(self.style_variations[style]['bottoms'])

        # Create OutfitComponent instances
        top = OutfitComponent(
            type=top_data['type'],
            color=top_data['color'],
            material=top_data['material'],
            fit='comfortable',
            style=style
        )

        bottom = OutfitComponent(
            type=bottom_data['type'],
            color=bottom_data['color'],
            material=bottom_data['material'],
            fit='fitted',
            style=style
        )

        # Enforce user color/material preferences
        if user_profile['favorite_colors']:
            if top.color not in user_profile['favorite_colors']:
                top.color = random.choice(user_profile['favorite_colors'])
            if bottom.color not in user_profile['favorite_colors']:
                bottom.color = random.choice(user_profile['favorite_colors'])

        if user_profile['preferred_materials']:
            if top.material not in user_profile['preferred_materials']:
                top.material = random.choice(user_profile['preferred_materials'])
            if bottom.material not in user_profile['preferred_materials']:
                bottom.material = random.choice(user_profile['preferred_materials'])

        # Handle coverage interplay
        interplay = user_profile['coverage_interplay']
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

        # Generate shoes
        shoes_data = random.choice(self.style_variations[style]['shoes'])
        shoes = OutfitComponent(
            type=shoes_data['type'],
            color=shoes_data['color'],
            material=shoes_data['material'],
            fit='comfortable',
            style=style
        )

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

        return OutfitData(
            top=top,
            bottom=bottom,
            shoes=shoes,
            extras=extras,
            style={'formal': 8 if style == 'formal' else 3, 'classic': 7, 'elegant': 9 if style == 'formal' else 4},
            colors=[top.color, bottom.color],
            materials=[top.material, bottom.material, shoes.material],
            suitable_for=[event],
            occasion=event,
            season=real_world_context.get('season', 'all') if real_world_context else 'all',
            formality_level=real_world_context.get('formality', 5) if real_world_context else 5,
            comfort_level=8
        )

    def generate_outfit(self, event: str, num_outfits: int, variations_per_outfit: int,
                       is_character_outfit: bool = False,
                       character_context: Optional[Dict] = None,
                       real_world_context: Optional[Dict] = None,
                       style_expression: Optional[str] = None,
                       user_name: Optional[str] = None,
                       max_retries: int = 3) -> List[OutfitData]:
        """Generate outfits based on the given parameters."""
        outfits = []
        
        for outfit_number in range(1, num_outfits + 1):
            for variation in range(1, variations_per_outfit + 1):
                retries = 0
                while retries < max_retries:
                    try:
                        # Generate outfit data
                        outfit_data = self._generate_outfit_data(
                            event, outfit_number, variation,
                            is_character_outfit, character_context,
                            real_world_context, style_expression,
                            user_name
                        )
                        
                        # Check for missing components
                        missing_components = self._get_missing_components(outfit_data)
                        if missing_components:
                            for component in missing_components:
                                logger.info(f"Attempting to generate missing {component}")
                                generated_component = self._generate_missing_component(component, outfit_data)
                                if generated_component and not generated_component.startswith("Please provide"):
                                    outfit_data[component] = generated_component
                                else:
                                    logger.error(f"Failed to generate valid {component}")
                                    break
                        
                        # Validate the outfit
                        if self._validate_outfit_data(outfit_data):
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
        return [comp for comp in required_components if comp not in outfit_data]

    def _generate_missing_component(self, component: str, outfit_data: OutfitData) -> Optional[Dict]:
        """Generate a missing component based on the existing outfit data."""
        style = 'formal' if outfit_data.formality_level >= 7 else 'casual'
        return random.choice(self.style_variations[style][f'{component}s'])

    def _validate_outfit_data(self, outfit_data: OutfitData) -> bool:
        """Validate the outfit data."""
        required_components = ['top', 'bottom', 'shoes']
        return all(comp in outfit_data for comp in required_components)