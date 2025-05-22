"""
Material and Texture Specifications for Fashion Outfit Generator.
Provides detailed specifications for materials and textures used in outfit generation.
"""

from typing import Dict, List, Set, Any
from material_models import MaterialDetail, TextureDetail, FabricCombination

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
            },
            'denim': {
                'properties': ['durable', 'structured', 'casual'],
                'light_behavior': 'matte with subtle highlights',
                'draping': 'structured, holds shape',
                'surface_characteristics': ['textured', 'sturdy', 'casual'],
                'construction_notes': 'requires strong needles, seams',
                'care_instructions': 'machine wash cold, tumble dry low'
            },
            'linen': {
                'properties': ['breathable', 'lightweight', 'natural'],
                'light_behavior': 'matte, crisp highlights',
                'draping': 'crisp, natural drape',
                'surface_characteristics': ['slightly textured', 'cool', 'natural'],
                'construction_notes': 'frays easily, pre-wash recommended',
                'care_instructions': 'machine wash gentle, iron while damp'
            },
            'cashmere': {
                'properties': ['soft', 'luxurious', 'warm'],
                'light_behavior': 'soft matte with subtle sheen',
                'draping': 'fluid, soft drape',
                'surface_characteristics': ['plush', 'fine', 'warm'],
                'construction_notes': 'delicate, requires gentle handling',
                'care_instructions': 'hand wash cold or dry clean'
            },
            'synthetic': {
                'properties': ['versatile', 'durable', 'affordable'],
                'light_behavior': 'varies, often matte or semi-shiny',
                'draping': 'varies by blend',
                'surface_characteristics': ['smooth', 'varied', 'resilient'],
                'construction_notes': 'easy to sew, resists wrinkles',
                'care_instructions': 'machine wash, tumble dry low'
            },
            'modal': {
                'properties': ['soft', 'breathable', 'drapey'],
                'light_behavior': 'soft matte',
                'draping': 'fluid, excellent drape',
                'surface_characteristics': ['smooth', 'cool', 'soft'],
                'construction_notes': 'easy to sew, blends well',
                'care_instructions': 'machine wash cold, gentle cycle'
            },
            'bamboo': {
                'properties': ['eco-friendly', 'soft', 'breathable'],
                'light_behavior': 'soft matte',
                'draping': 'fluid, soft drape',
                'surface_characteristics': ['smooth', 'cool', 'natural'],
                'construction_notes': 'easy to sew, sustainable',
                'care_instructions': 'machine wash cold, gentle cycle'
            },
            'sequin': {
                'properties': ['shiny', 'decorative', 'party'],
                'light_behavior': 'highly reflective, sparkly',
                'draping': 'stiff, holds shape',
                'surface_characteristics': ['textured', 'shiny', 'eye-catching'],
                'construction_notes': 'requires careful stitching, can snag',
                'care_instructions': 'hand wash, avoid wringing'
            },
            'satin': {
                'properties': ['shiny', 'smooth', 'elegant'],
                'light_behavior': 'high sheen, reflective',
                'draping': 'fluid, elegant drape',
                'surface_characteristics': ['smooth', 'shiny', 'luxurious'],
                'construction_notes': 'slippery, pins recommended',
                'care_instructions': 'dry clean or gentle hand wash'
            },
            'suede': {
                'properties': ['soft', 'matte', 'luxurious'],
                'light_behavior': 'matte, absorbs light',
                'draping': 'structured, soft hand',
                'surface_characteristics': ['napped', 'soft', 'rich'],
                'construction_notes': 'requires special needles, avoid water',
                'care_instructions': 'brush clean, avoid water'
            },
            'mesh': {
                'properties': ['breathable', 'lightweight', 'see-through'],
                'light_behavior': 'translucent, diffuses light',
                'draping': 'fluid, flexible',
                'surface_characteristics': ['open weave', 'light', 'airy'],
                'construction_notes': 'can stretch, use stabilizer',
                'care_instructions': 'hand wash, air dry'
            },
            'fleece': {
                'properties': ['warm', 'soft', 'insulating'],
                'light_behavior': 'matte, absorbs light',
                'draping': 'structured, soft',
                'surface_characteristics': ['plush', 'soft', 'thick'],
                'construction_notes': 'easy to sew, edges do not fray',
                'care_instructions': 'machine wash cold, tumble dry low'
            },
            'brocade': {
                'properties': ['ornate', 'structured', 'luxurious'],
                'light_behavior': 'textured with pattern highlights',
                'draping': 'structured with pattern definition',
                'surface_characteristics': ['ornate', 'textured', 'rich'],
                'construction_notes': 'requires pattern matching',
                'care_instructions': 'dry clean only'
            },
            'jacquard': {
                'properties': ['patterned', 'structured', 'elegant'],
                'light_behavior': 'varies with pattern',
                'draping': 'structured with pattern definition',
                'surface_characteristics': ['patterned', 'textured', 'rich'],
                'construction_notes': 'requires pattern matching',
                'care_instructions': 'dry clean recommended'
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
            },
            'ribbed': {
                'visual_properties': ['vertical lines', 'stretchy'],
                'light_interaction': 'creates subtle shadow lines',
                'movement_characteristics': 'flexible, hugs body',
                'construction_notes': 'requires rib knit technique',
                'care_instructions': 'machine wash gentle'
            },
            'seersucker': {
                'visual_properties': ['puckered texture', 'striped'],
                'light_interaction': 'diffuses light, matte',
                'movement_characteristics': 'light, airy',
                'construction_notes': 'woven for puckered effect',
                'care_instructions': 'machine wash cold'
            },
            'brocade': {
                'visual_properties': ['raised pattern', 'ornate'],
                'light_interaction': 'reflective highlights on pattern',
                'movement_characteristics': 'structured, holds shape',
                'construction_notes': 'requires careful pattern matching',
                'care_instructions': 'dry clean only'
            },
            'jacquard': {
                'visual_properties': ['woven pattern', 'complex'],
                'light_interaction': 'patterned light reflection',
                'movement_characteristics': 'varies, often structured',
                'construction_notes': 'complex weaving, frays easily',
                'care_instructions': 'dry clean or gentle wash'
            },
            'sequin': {
                'visual_properties': ['shiny discs', 'reflective'],
                'light_interaction': 'sparkles, high reflection',
                'movement_characteristics': 'stiff, holds shape',
                'construction_notes': 'hand sew sequins, can snag',
                'care_instructions': 'hand wash, avoid wringing'
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

    def get_material_detail(self, material: str) -> MaterialDetail:
        """Get material details as a Pydantic model."""
        if material not in self.material_properties:
            raise ValueError(f"Material {material} not found")
        props = self.material_properties[material]
        return MaterialDetail(**props)

    def get_texture_detail(self, texture: str) -> TextureDetail:
        """Get texture details as a Pydantic model."""
        if texture not in self.texture_properties:
            raise ValueError(f"Texture {texture} not found")
        props = self.texture_properties[texture]
        return TextureDetail(**props)

    def get_material_properties(self, material: str) -> Dict:
        """Get raw material properties dictionary."""
        return self.material_properties.get(material, {})

    def get_texture_properties(self, texture: str) -> Dict:
        """Get raw texture properties dictionary."""
        return self.texture_properties.get(texture, {})

    def get_light_behavior(self, material: str) -> str:
        """Get light behavior description for a material."""
        return self.material_properties.get(material, {}).get('light_behavior', '')

    def get_draping_behavior(self, material: str) -> str:
        """Get draping behavior description for a material."""
        return self.material_properties.get(material, {}).get('draping', '')

    def get_surface_characteristics(self, material: str) -> List[str]:
        """Get surface characteristics for a material."""
        return self.material_properties.get(material, {}).get('surface_characteristics', [])

    def get_construction_notes(self, material: str) -> str:
        """Get construction notes for a material."""
        return self.material_properties.get(material, {}).get('construction_notes', '')

    def get_care_instructions(self, material: str) -> str:
        """Get care instructions for a material."""
        return self.material_properties.get(material, {}).get('care_instructions', '')

    def get_materials_for_season(self, season: str) -> List[str]:
        """Get suitable materials for a given season."""
        season_materials = {
            'summer': ['cotton', 'linen', 'silk', 'synthetic'],
            'winter': ['wool', 'cashmere', 'velvet', 'leather'],
            'spring': ['cotton', 'silk', 'linen', 'lace'],
            'fall': ['wool', 'leather', 'denim', 'velvet']
        }
        return season_materials.get(season.lower(), [])

    def get_materials_for_formality(self, formality: str) -> List[str]:
        """Return materials suitable for a given formality level."""
        formality = formality.lower()
        if formality in ['formal', 'black tie']:
            return ['silk', 'satin', 'velvet', 'lace', 'brocade', 'jacquard']
        elif formality in ['business', 'semi-formal']:
            return ['wool', 'cotton', 'linen', 'silk', 'denim']
        else:
            return ['cotton', 'denim', 'linen', 'synthetic', 'mesh']

    def get_textures_for_material(self, material: str) -> List[str]:
        """Return textures commonly used with a material."""
        material_texture_map = {
            'cotton': ['ribbed', 'pleated', 'quilted', 'seersucker'],
            'silk': ['pleated', 'satin', 'jacquard'],
            'wool': ['knit', 'ribbed'],
            'denim': ['quilted', 'ribbed'],
            'leather': ['embossed'],
            'velvet': ['pleated'],
            'lace': ['brocade'],
            'linen': ['seersucker'],
            'satin': ['pleated'],
            'suede': ['embossed'],
            'mesh': ['mesh', 'sequin'],
            'fleece': ['quilted'],
        }
        return [t for t in material_texture_map.get(material, []) if t in self.texture_properties]

    def recommend_materials(self, season: str, formality: str) -> List[str]:
        """Recommend materials based on season and formality."""
        season = season.lower()
        formality = formality.lower()
        
        # Get materials for season and formality
        season_materials = set(self.get_materials_for_season(season))
        formality_materials = set(self.get_materials_for_formality(formality))
        
        # First try to get materials that work for both season and formality
        recommended = list(season_materials & formality_materials)
        
        # If no overlap, prioritize seasonal materials for casual outfits
        if not recommended and formality in ['casual']:
            recommended = list(season_materials)
        
        # If still no materials, use formality-based materials
        if not recommended:
            recommended = list(formality_materials)
        
        # If still no materials, use safe defaults based on season
        if not recommended:
            if season == 'winter':
                recommended = ['wool', 'cashmere', 'fleece']
            elif season == 'summer':
                recommended = ['cotton', 'linen', 'silk']
            elif season == 'spring':
                recommended = ['cotton', 'linen', 'silk']
            elif season == 'fall':
                recommended = ['wool', 'cotton', 'denim']
            else:
                recommended = ['cotton', 'synthetic']
        
        return recommended

# Material specifications with enhanced properties
HAUTE_COUTURE_MATERIALS: Dict[str, Dict[str, Any]] = {
    'luxury_fabrics': {
        'silk': {
            'types': ['charmeuse', 'crepe', 'duchesse', 'georgette', 'organza', 'satin', 'taffeta'],
            'properties': [
                'natural fiber',
                'breathable',
                'temperature regulating',
                'elegant drape',
                'subtle sheen'
            ],
            'usage': 'dresses, blouses, linings',
            'color': {
                'primary': '#FFFFFF',
                'secondary': None,
                'accent': None,
                'metallic': False,
                'iridescent': True,
                'opacity': 0.9,
                'light_reflection': 'subtle sheen'
            },
            'texture': {
                'type': 'smooth',
                'pattern': None,
                'pattern_scale': None,
                'embossed': False,
                'quilted': False,
                'surface_finish': 'lustrous'
            },
            'physical': {
                'weight': 45.0,  # g/m²
                'thickness': 0.1,  # mm
                'stretch': 2.0,  # percentage
                'drape': 'fluid',
                'breathability': 8,
                'thermal_properties': 'temperature regulating',
                'sound': 'soft rustle'
            },
            'sustainability': {
                'origin': 'China',
                'certifications': ['OEKO-TEX', 'GOTS'],
                'recycled_content': 0.0,
                'organic': False,
                'vegan': False,
                'cruelty_free': False,
                'supplier': 'Luxury Silk Mills'
            },
            'care': {
                'washing': 'Dry clean only',
                'drying': 'Lay flat',
                'ironing': 'Low heat, steam',
                'dry_cleaning': 'Recommended',
                'special_instructions': [
                    'Avoid direct sunlight',
                    'Store in breathable container'
                ],
                'aging_characteristics': 'Develops patina over time'
            },
            'digital': {
                'pbr_params': {
                    'roughness': 0.2,
                    'metallic': 0.0,
                    'specular': 0.5
                },
                'texture_maps': {
                    'albedo': 'silk_albedo.png',
                    'normal': 'silk_normal.png',
                    'roughness': 'silk_roughness.png'
                },
                'swatch_url': 'https://example.com/silk_swatch',
                'preview_url': 'https://example.com/silk_preview'
            },
            'finish': 'natural',
            'construction_notes': 'Requires French seams for durability',
            'quality_grade': 'A+',
            'seasonal_suitability': ['spring', 'summer', 'fall'],
            'durability': 7
        },
        'lace': {
            'types': ['chantilly', 'guipure', 'alengon', 'venise', 'point'],
            'properties': [
                'delicate',
                'intricate patterns',
                'sheer',
                'elegant',
                'feminine'
            ],
            'usage': 'overlays, trims, veils',
            'color': {
                'primary': '#FFFFFF',
                'secondary': None,
                'accent': None,
                'metallic': False,
                'iridescent': False,
                'opacity': 0.7,
                'light_reflection': 'matte'
            },
            'texture': {
                'type': 'patterned',
                'pattern': 'floral',
                'pattern_scale': 'medium',
                'embossed': False,
                'quilted': False,
                'surface_finish': 'textured'
            },
            'physical': {
                'weight': 35.0,
                'thickness': 0.2,
                'stretch': 0.0,
                'drape': 'structured',
                'breathability': 9,
                'thermal_properties': 'light',
                'sound': 'crisp'
            },
            'sustainability': {
                'origin': 'France',
                'certifications': ['OEKO-TEX'],
                'recycled_content': 0.0,
                'organic': False,
                'vegan': True,
                'cruelty_free': True,
                'supplier': 'French Lace House'
            },
            'care': {
                'washing': 'Hand wash',
                'drying': 'Lay flat',
                'ironing': 'Low heat, no steam',
                'dry_cleaning': 'Not recommended',
                'special_instructions': [
                    'Store flat',
                    'Avoid snags'
                ],
                'aging_characteristics': 'Maintains structure'
            },
            'digital': {
                'pbr_params': {
                    'roughness': 0.4,
                    'metallic': 0.0,
                    'specular': 0.3
                },
                'texture_maps': {
                    'albedo': 'lace_albedo.png',
                    'normal': 'lace_normal.png',
                    'roughness': 'lace_roughness.png'
                },
                'swatch_url': 'https://example.com/lace_swatch',
                'preview_url': 'https://example.com/lace_preview'
            },
            'finish': 'natural',
            'construction_notes': 'Requires careful handling and specialized needles',
            'quality_grade': 'A',
            'seasonal_suitability': ['spring', 'summer'],
            'durability': 6
        },
        'velvet': {
            'types': ['silk', 'cotton', 'synthetic', 'crushed', 'panne'],
            'properties': [
                'plush',
                'rich texture',
                'dramatic drape',
                'luxurious',
                'dense pile'
            ],
            'usage': 'evening wear, upholstery, accessories',
            'color': {
                'primary': '#000000',
                'secondary': None,
                'accent': None,
                'metallic': False,
                'iridescent': True,
                'opacity': 1.0,
                'light_reflection': 'directional'
            },
            'texture': {
                'type': 'plush',
                'pattern': None,
                'pattern_scale': None,
                'embossed': False,
                'quilted': False,
                'surface_finish': 'pile'
            },
            'physical': {
                'weight': 280.0,
                'thickness': 1.5,
                'stretch': 1.0,
                'drape': 'structured',
                'breathability': 5,
                'thermal_properties': 'insulating',
                'sound': 'muted'
            },
            'sustainability': {
                'origin': 'Italy',
                'certifications': ['OEKO-TEX'],
                'recycled_content': 0.0,
                'organic': False,
                'vegan': False,
                'cruelty_free': True,
                'supplier': 'Italian Velvet Mills'
            },
            'care': {
                'washing': 'Dry clean only',
                'drying': 'Hang',
                'ironing': 'Steam only',
                'dry_cleaning': 'Recommended',
                'special_instructions': [
                    'Brush with velvet brush',
                    'Store hanging'
                ],
                'aging_characteristics': 'Develops patina'
            },
            'digital': {
                'pbr_params': {
                    'roughness': 0.8,
                    'metallic': 0.0,
                    'specular': 0.2
                },
                'texture_maps': {
                    'albedo': 'velvet_albedo.png',
                    'normal': 'velvet_normal.png',
                    'roughness': 'velvet_roughness.png'
                },
                'swatch_url': 'https://example.com/velvet_swatch',
                'preview_url': 'https://example.com/velvet_preview'
            },
            'finish': 'natural',
            'construction_notes': 'Requires careful pressing and handling',
            'quality_grade': 'A+',
            'seasonal_suitability': ['fall', 'winter'],
            'durability': 8
        }
    }
} 