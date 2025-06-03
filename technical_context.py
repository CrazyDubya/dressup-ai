"""
Technical and Environmental Context Specifications for Fashion Outfit Generator.
Provides detailed specifications for photography, lighting, and environmental context.
"""

from typing import Dict, List, Set
from enum import Enum

class LightingSetup(Enum):
    """Types of lighting setups for fashion photography."""
    THREE_POINT = "three_point"
    RIM_LIGHT = "rim_light"
    SOFT_BOX = "soft_box"
    NATURAL = "natural"
    DRAMATIC = "dramatic"
    HIGH_FASHION = "high_fashion"

class CameraAngle(Enum):
    """Types of camera angles for fashion photography."""
    THREE_QUARTER = "three_quarter"
    FULL_LENGTH = "full_length"
    CLOSE_UP = "close_up"
    DETAIL = "detail"
    ENVIRONMENTAL = "environmental"

class TechnicalContext:
    """Manages technical and environmental context specifications."""
    
    def __init__(self):
        self.lighting_setups = {
            LightingSetup.THREE_POINT: {
                'description': 'Classic three-point lighting with key, fill, and rim lights',
                'equipment': ['key light', 'fill light', 'rim light'],
                'mood': 'balanced and professional',
                'best_for': ['portraits', 'full-body shots', 'product details']
            },
            LightingSetup.RIM_LIGHT: {
                'description': 'Dramatic rim lighting with strong backlight',
                'equipment': ['backlight', 'fill light'],
                'mood': 'dramatic and edgy',
                'best_for': ['silhouettes', 'dramatic shots', 'texture emphasis']
            },
            LightingSetup.SOFT_BOX: {
                'description': 'Soft, diffused lighting for even illumination',
                'equipment': ['soft box', 'fill light'],
                'mood': 'soft and flattering',
                'best_for': ['portraits', 'delicate fabrics', 'subtle textures']
            },
            LightingSetup.NATURAL: {
                'description': 'Natural lighting with minimal artificial light',
                'equipment': ['reflector', 'diffuser'],
                'mood': 'natural and authentic',
                'best_for': ['lifestyle shots', 'outdoor settings', 'natural fabrics']
            },
            LightingSetup.DRAMATIC: {
                'description': 'High-contrast lighting with strong shadows',
                'equipment': ['spot light', 'gobo', 'reflector'],
                'mood': 'dramatic and intense',
                'best_for': ['editorial shots', 'bold designs', 'texture emphasis']
            },
            LightingSetup.HIGH_FASHION: {
                'description': 'Sophisticated lighting setup for high-end fashion',
                'equipment': ['multiple lights', 'reflectors', 'diffusers'],
                'mood': 'luxurious and refined',
                'best_for': ['high-end fashion', 'luxury items', 'detailed shots']
            }
        }
        
        self.camera_angles = {
            CameraAngle.THREE_QUARTER: {
                'description': 'Three-quarter view showing outfit details',
                'composition': 'balanced with good depth',
                'best_for': ['full outfits', 'proportions', 'overall look']
            },
            CameraAngle.FULL_LENGTH: {
                'description': 'Full-length shot showing complete outfit',
                'composition': 'vertical with good proportions',
                'best_for': ['complete looks', 'proportions', 'overall style']
            },
            CameraAngle.CLOSE_UP: {
                'description': 'Close-up shot focusing on details',
                'composition': 'tight framing on specific elements',
                'best_for': ['details', 'textures', 'accessories']
            },
            CameraAngle.DETAIL: {
                'description': 'Extreme close-up of specific details',
                'composition': 'very tight framing',
                'best_for': ['fabric details', 'construction', 'textures']
            },
            CameraAngle.ENVIRONMENTAL: {
                'description': 'Shot showing outfit in context',
                'composition': 'wide framing with context',
                'best_for': ['lifestyle shots', 'context', 'setting']
            }
        }
        
        self.environmental_contexts = {
            'studio': {
                'lighting': 'controlled studio lighting',
                'background': 'clean, neutral background',
                'mood': 'professional and clean',
                'best_for': ['product shots', 'clean looks', 'detailed shots']
            },
            'urban': {
                'lighting': 'natural and artificial light mix',
                'background': 'city elements and architecture',
                'mood': 'modern and dynamic',
                'best_for': ['street style', 'urban fashion', 'lifestyle shots']
            },
            'natural': {
                'lighting': 'natural light with reflectors',
                'background': 'natural elements and landscapes',
                'mood': 'organic and authentic',
                'best_for': ['natural fabrics', 'outdoor wear', 'lifestyle shots']
            },
            'luxury': {
                'lighting': 'sophisticated lighting setup',
                'background': 'luxurious settings and elements',
                'mood': 'elegant and refined',
                'best_for': ['high-end fashion', 'luxury items', 'editorial shots']
            }
        }
        
        self.technical_requirements = {
            'resolution': {
                'minimum': '3000x2000 pixels',
                'recommended': '6000x4000 pixels',
                'aspect_ratio': '3:2 or 4:3'
            },
            'color_depth': {
                'minimum': '8-bit',
                'recommended': '16-bit',
                'color_space': 'sRGB or Adobe RGB'
            },
            'focus': {
                'type': 'autofocus with manual override',
                'points': 'multiple focus points',
                'mode': 'continuous autofocus'
            },
            'exposure': {
                'mode': 'manual or aperture priority',
                'metering': 'matrix/evaluative',
                'compensation': '±3 stops'
            }
        }

    def get_lighting_setup(self, setup: LightingSetup) -> Dict:
        """Get specifications for a specific lighting setup."""
        return self.lighting_setups.get(setup, {})

    def get_camera_angle(self, angle: CameraAngle) -> Dict:
        """Get specifications for a specific camera angle."""
        return self.camera_angles.get(angle, {})

    def get_environmental_context(self, context: str) -> Dict:
        """Get specifications for a specific environmental context."""
        return self.environmental_contexts.get(context, {})

    def get_technical_requirements(self) -> Dict:
        """Get technical requirements for photography."""
        return self.technical_requirements

    def compose_technical_prompt(self, outfit_data: Dict) -> str:
        """Compose a technical prompt for photography."""
        # Select appropriate lighting setup based on outfit style
        style = outfit_data.get('style', 'casual')
        if style in ['formal', 'luxury']:
            lighting = LightingSetup.HIGH_FASHION
        elif style in ['dramatic', 'edgy']:
            lighting = LightingSetup.DRAMATIC
        else:
            lighting = LightingSetup.THREE_POINT
        
        # Select appropriate camera angle based on outfit type
        if 'full_length' in outfit_data.get('requirements', []):
            angle = CameraAngle.FULL_LENGTH
        elif 'details' in outfit_data.get('requirements', []):
            angle = CameraAngle.DETAIL
        else:
            angle = CameraAngle.THREE_QUARTER
        
        # Get specifications
        lighting_specs = self.get_lighting_setup(lighting)
        angle_specs = self.get_camera_angle(angle)
        tech_specs = self.get_technical_requirements()
        
        # Compose prompt
        prompt = f"""
        TECHNICAL SPECIFICATIONS:
        
        LIGHTING:
        - Setup: {lighting_specs['description']}
        - Equipment: {', '.join(lighting_specs['equipment'])}
        - Mood: {lighting_specs['mood']}
        
        CAMERA:
        - Angle: {angle_specs['description']}
        - Composition: {angle_specs['composition']}
        - Best for: {angle_specs['best_for']}
        
        TECHNICAL REQUIREMENTS:
        - Resolution: {tech_specs['resolution']['recommended']}
        - Color Depth: {tech_specs['color_depth']['recommended']}
        - Focus: {tech_specs['focus']['type']}
        - Exposure: {tech_specs['exposure']['mode']}
        """
        
        return prompt

    def compose_environmental_prompt(self, outfit_data: Dict) -> str:
        """Compose an environmental prompt for photography."""
        # Select appropriate environmental context
        style = outfit_data.get('style', 'casual')
        if style in ['formal', 'luxury']:
            context = 'luxury'
        elif style in ['casual', 'street']:
            context = 'urban'
        elif style in ['natural', 'bohemian']:
            context = 'natural'
        else:
            context = 'studio'
        
        # Get specifications
        env_specs = self.get_environmental_context(context)
        
        # Compose prompt
        prompt = f"""
        ENVIRONMENTAL CONTEXT:
        
        SETTING:
        - Type: {context}
        - Lighting: {env_specs['lighting']}
        - Background: {env_specs['background']}
        - Mood: {env_specs['mood']}
        - Best for: {env_specs['best_for']}
        """
        
        return prompt 
