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

    def get_materials_for_season(self, season: str) -> List[str]:
        """Return materials suitable for a given season."""
        season = season.lower()
        season_map = {
            'summer': ['cotton', 'linen', 'silk', 'bamboo', 'modal', 'mesh'],
            'winter': ['wool', 'cashmere', 'fleece', 'velvet', 'leather', 'suede'],
            'spring': ['cotton', 'linen', 'silk', 'bamboo', 'modal', 'denim'],
            'fall': ['wool', 'cotton', 'denim', 'leather', 'suede', 'velvet']
        }
        return [m for m in season_map.get(season, []) if m in self.material_properties]

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