"""
Material and Texture Specifications for Fashion Outfit Generator.
Provides detailed specifications for materials and textures used in outfit generation.
"""

from typing import Dict, List, Set

class MaterialSpecifications:
    """Detailed specifications for different materials."""
    
    def __init__(self):
        self.material_properties = {
            'silk': {
                'properties': ['lustrous', 'smooth', 'flowing'],
                'light_behavior': 'subtle sheen with dynamic light response',
                'draping': 'elegant natural drape with fluid movement',
                'surface_characteristics': ['smooth', 'shiny', 'delicate'],
                'construction_notes': 'requires careful handling and precise stitching',
                'care_instructions': 'dry clean only, avoid direct sunlight'
            },
            'wool': {
                'properties': ['textured', 'warm', 'structured'],
                'light_behavior': 'matte finish with depth in shadows',
                'draping': 'structured drape with natural body',
                'surface_characteristics': ['soft', 'textured', 'warm'],
                'construction_notes': 'excellent for tailored pieces',
                'care_instructions': 'dry clean or hand wash in cold water'
            },
            'cotton': {
                'properties': ['breathable', 'durable', 'versatile'],
                'light_behavior': 'matte finish with natural texture',
                'draping': 'casual drape with good structure',
                'surface_characteristics': ['soft', 'natural', 'breathable'],
                'construction_notes': 'easy to work with, versatile',
                'care_instructions': 'machine washable, can be ironed'
            },
            'leather': {
                'properties': ['durable', 'luxurious', 'structured'],
                'light_behavior': 'rich sheen with depth',
                'draping': 'structured with minimal drape',
                'surface_characteristics': ['smooth', 'rich', 'durable'],
                'construction_notes': 'requires specialized equipment',
                'care_instructions': 'professional cleaning recommended'
            },
            'velvet': {
                'properties': ['luxurious', 'textured', 'rich'],
                'light_behavior': 'directional sheen with depth',
                'draping': 'rich drape with body',
                'surface_characteristics': ['plush', 'rich', 'directional'],
                'construction_notes': 'requires careful handling',
                'care_instructions': 'dry clean only, avoid crushing'
            },
            'lace': {
                'properties': ['delicate', 'ornate', 'feminine'],
                'light_behavior': 'translucent with pattern play',
                'draping': 'delicate drape with structure',
                'surface_characteristics': ['delicate', 'ornate', 'translucent'],
                'construction_notes': 'requires careful handling',
                'care_instructions': 'hand wash or dry clean'
            }
        }
        
        self.texture_properties = {
            'pleated': {
                'visual_properties': ['regular folds', 'geometric rhythm'],
                'light_interaction': 'creates regular light and shadow patterns',
                'movement_characteristics': 'accordion-like flexibility',
                'construction_notes': 'requires precise pleating and pressing',
                'care_instructions': 'dry clean to maintain pleats'
            },
            'quilted': {
                'visual_properties': ['dimensional texture', 'geometric patterns'],
                'light_interaction': 'creates depth through shadow play',
                'movement_characteristics': 'structured with subtle dimension',
                'construction_notes': 'requires precise stitching',
                'care_instructions': 'gentle machine wash or dry clean'
            },
            'embossed': {
                'visual_properties': ['raised pattern', 'textured surface'],
                'light_interaction': 'creates depth through raised elements',
                'movement_characteristics': 'structured with pattern definition',
                'construction_notes': 'requires specialized equipment',
                'care_instructions': 'dry clean to maintain pattern'
            },
            'knit': {
                'visual_properties': ['textured surface', 'flexible structure'],
                'light_interaction': 'creates depth through stitch definition',
                'movement_characteristics': 'flexible with good drape',
                'construction_notes': 'requires specialized equipment',
                'care_instructions': 'hand wash or gentle machine wash'
            }
        }
        
        self.material_combinations = {
            'luxe_mix': {
                'materials': ['silk', 'cashmere', 'leather'],
                'characteristics': ['luxurious', 'sophisticated', 'rich'],
                'light_behavior': 'complex interplay of sheens and textures',
                'draping': 'varied drape with rich dimension'
            },
            'natural_blend': {
                'materials': ['cotton', 'linen', 'wool'],
                'characteristics': ['natural', 'breathable', 'versatile'],
                'light_behavior': 'matte finish with natural texture',
                'draping': 'casual drape with good structure'
            },
            'textural_contrast': {
                'materials': ['velvet', 'satin', 'lace'],
                'characteristics': ['rich', 'varied', 'feminine'],
                'light_behavior': 'complex interplay of sheens',
                'draping': 'varied drape with rich dimension'
            }
        }

    def get_material_properties(self, material: str) -> Dict:
        """Get detailed properties for a specific material."""
        return self.material_properties.get(material, {})

    def get_texture_properties(self, texture: str) -> Dict:
        """Get detailed properties for a specific texture."""
        return self.texture_properties.get(texture, {})

    def get_material_combination(self, combination: str) -> Dict:
        """Get detailed properties for a specific material combination."""
        return self.material_combinations.get(combination, {})

    def get_light_behavior(self, material: str) -> str:
        """Get light behavior description for a material."""
        props = self.get_material_properties(material)
        return props.get('light_behavior', 'standard light interaction')

    def get_draping_behavior(self, material: str) -> str:
        """Get draping behavior description for a material."""
        props = self.get_material_properties(material)
        return props.get('draping', 'standard drape')

    def get_surface_characteristics(self, material: str) -> List[str]:
        """Get surface characteristics for a material."""
        props = self.get_material_properties(material)
        return props.get('surface_characteristics', [])

    def get_construction_notes(self, material: str) -> str:
        """Get construction notes for a material."""
        props = self.get_material_properties(material)
        return props.get('construction_notes', 'standard construction')

    def get_care_instructions(self, material: str) -> str:
        """Get care instructions for a material."""
        props = self.get_material_properties(material)
        return props.get('care_instructions', 'standard care') 