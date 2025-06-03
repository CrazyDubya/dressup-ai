"""
Style and Cultural Context Specifications for Fashion Outfit Generator.
Provides detailed specifications for style categories and cultural contexts.
"""

from typing import Dict, List, Set
from enum import Enum

class Style(Enum):
    """Style categories for outfit classification."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FORMAL = "formal"
    ATHLETIC = "athletic"
    BOHEMIAN = "bohemian"
    MINIMALIST = "minimalist"
    GLAMOROUS = "glamorous"
    EDGY = "edgy"
    ROMANTIC = "romantic"
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    BOLD = "bold"
    PROVOCATIVE = "provocative"
    FANTASY = "fantasy"
    HISTORICAL = "historical"
    NOBLE = "noble"
    COMMONER = "commoner"
    COURT = "court"
    ADVENTURE = "adventure"
    CEREMONIAL = "ceremonial"

class StyleContext:
    """Manages style and cultural context specifications."""
    
    def __init__(self):
        self.style_keywords = {
            Style.PROFESSIONAL: {
                'keywords': {'business', 'professional', 'office', 'corporate', 'tailored', 
                           'structured', 'executive', 'formal', 'suit', 'blazer', 'power',
                           'authoritative', 'polished', 'refined'},
                'materials': ['wool', 'cotton', 'silk', 'polyester'],
                'colors': ['navy', 'black', 'gray', 'white', 'burgundy'],
                'construction': ['tailored', 'structured', 'precise'],
                'details': ['minimal', 'refined', 'professional']
            },
            Style.CASUAL: {
                'keywords': {'casual', 'relaxed', 'comfortable', 'everyday', 'laid-back', 
                           'easygoing', 'weekend', 'leisure', 'informal', 'sporty',
                           'approachable', 'authentic', 'relatable'},
                'materials': ['cotton', 'denim', 'knit', 'linen'],
                'colors': ['blue', 'white', 'gray', 'black', 'navy'],
                'construction': ['relaxed', 'comfortable', 'easy'],
                'details': ['simple', 'functional', 'practical']
            },
            Style.FORMAL: {
                'keywords': {'formal', 'elegant', 'sophisticated', 'luxury', 'black-tie', 
                           'gown', 'evening', 'dressy', 'chic', 'refined', 'ceremonial',
                           'distinguished', 'regal'},
                'materials': ['silk', 'velvet', 'lace', 'satin'],
                'colors': ['black', 'navy', 'burgundy', 'emerald'],
                'construction': ['precise', 'elegant', 'sophisticated'],
                'details': ['luxurious', 'refined', 'elegant']
            },
            Style.BOHEMIAN: {
                'keywords': {'bohemian', 'boho', 'flowy', 'earthy', 'artistic', 
                           'free-spirited', 'hippie', 'eclectic', 'natural', 'organic',
                           'wanderer', 'artist', 'unconventional'},
                'materials': ['cotton', 'linen', 'silk', 'lace'],
                'colors': ['earth tones', 'jewel tones', 'pastels'],
                'construction': ['flowing', 'relaxed', 'artistic'],
                'details': ['ornate', 'natural', 'artistic']
            }
        }
        
        self.cultural_rules = {
            'western': {
                'professional': {
                    'required': ['shirt', 'pants', 'shoes'],
                    'forbidden': ['shorts', 'sandals', 'tank_top'],
                    'materials': ['cotton', 'wool', 'silk'],
                    'colors': ['black', 'navy', 'gray', 'white']
                },
                'formal': {
                    'required': ['suit', 'dress_shirt', 'tie', 'dress_shoes'],
                    'forbidden': ['jeans', 'sneakers', 't_shirt'],
                    'materials': ['silk', 'wool', 'cashmere'],
                    'colors': ['black', 'navy', 'charcoal']
                }
            },
            'eastern': {
                'traditional': {
                    'required': ['kimono', 'obi', 'zori'],
                    'forbidden': ['western_clothing'],
                    'materials': ['silk', 'cotton'],
                    'colors': ['red', 'black', 'white', 'gold']
                },
                'formal': {
                    'required': ['haori', 'hakama', 'tabi'],
                    'forbidden': ['casual_wear'],
                    'materials': ['silk', 'brocade'],
                    'colors': ['black', 'navy', 'gray']
                }
            }
        }
        
        self.seasonal_adaptations = {
            'winter': {
                'materials': {'wool', 'cashmere', 'fleece', 'down', 'faux fur'},
                'layers': {'coat', 'jacket', 'sweater', 'scarf', 'gloves'},
                'colors': {'deep', 'rich', 'dark', 'neutral'},
                'lengths': {'long', 'full-length', 'ankle-length'}
            },
            'spring': {
                'materials': {'cotton', 'linen', 'light wool', 'silk'},
                'layers': {'light jacket', 'cardigan', 'shawl'},
                'colors': {'pastel', 'light', 'fresh', 'floral'},
                'lengths': {'midi', 'knee-length', 'three-quarter'}
            },
            'summer': {
                'materials': {'cotton', 'linen', 'chiffon', 'silk'},
                'layers': {'light', 'minimal'},
                'colors': {'bright', 'light', 'vibrant'},
                'lengths': {'short', 'mini', 'cropped'}
            },
            'fall': {
                'materials': {'wool', 'tweed', 'corduroy', 'velvet'},
                'layers': {'jacket', 'sweater', 'vest'},
                'colors': {'earthy', 'warm', 'muted'},
                'lengths': {'midi', 'knee-length', 'ankle-length'}
            }
        }

    def get_style_keywords(self, style: Style) -> Dict:
        """Get keywords and specifications for a specific style."""
        return self.style_keywords.get(style, {})

    def get_cultural_rules(self, culture: str, style: str) -> Dict:
        """Get cultural rules for a specific culture and style."""
        return self.cultural_rules.get(culture, {}).get(style, {})

    def get_seasonal_adaptations(self, season: str) -> Dict:
        """Get seasonal adaptations for a specific season."""
        return self.seasonal_adaptations.get(season, {})

    def validate_style(self, outfit_data: Dict, style: Style) -> Dict:
        """Validate an outfit against a specific style."""
        style_specs = self.get_style_keywords(style)
        validation_results = {
            'is_valid': True,
            'score': 0,
            'violations': [],
            'suggestions': []
        }
        
        # Check materials
        outfit_materials = set(outfit_data.get('materials', []))
        style_materials = set(style_specs.get('materials', []))
        if not outfit_materials & style_materials:
            validation_results['violations'].append(
                f"Materials do not match {style.value} style"
            )
            validation_results['score'] -= 10
        
        # Check colors
        outfit_colors = set(outfit_data.get('colors', []))
        style_colors = set(style_specs.get('colors', []))
        if not outfit_colors & style_colors:
            validation_results['violations'].append(
                f"Colors do not match {style.value} style"
            )
            validation_results['score'] -= 10
        
        # Check construction
        outfit_construction = outfit_data.get('construction', '')
        style_construction = style_specs.get('construction', [])
        if not any(construct in outfit_construction.lower() 
                  for construct in style_construction):
            validation_results['violations'].append(
                f"Construction does not match {style.value} style"
            )
            validation_results['score'] -= 10
        
        # Generate suggestions based on violations
        if validation_results['violations']:
            validation_results['is_valid'] = False
            validation_results['suggestions'] = [
                f"Consider using {', '.join(style_materials)} for materials",
                f"Try incorporating {', '.join(style_colors)} for colors",
                f"Focus on {', '.join(style_construction)} construction"
            ]
        
        return validation_results

    def adapt_for_season(self, outfit_data: Dict, season: str) -> Dict:
        """Adapt an outfit for a specific season."""
        seasonal_specs = self.get_seasonal_adaptations(season)
        adaptation_results = {
            'adapted': False,
            'changes': [],
            'suggestions': []
        }
        
        # Check materials
        outfit_materials = set(outfit_data.get('materials', []))
        seasonal_materials = seasonal_specs.get('materials', set())
        if not outfit_materials & seasonal_materials:
            adaptation_results['changes'].append(
                f"Consider using {', '.join(seasonal_materials)} for {season}"
            )
        
        # Check layers
        outfit_layers = set(outfit_data.get('layers', []))
        seasonal_layers = seasonal_specs.get('layers', set())
        if not outfit_layers & seasonal_layers:
            adaptation_results['changes'].append(
                f"Consider adding {', '.join(seasonal_layers)} for {season}"
            )
        
        # Check colors
        outfit_colors = set(outfit_data.get('colors', []))
        seasonal_colors = seasonal_specs.get('colors', set())
        if not outfit_colors & seasonal_colors:
            adaptation_results['changes'].append(
                f"Consider using {', '.join(seasonal_colors)} colors for {season}"
            )
        
        # Check lengths
        outfit_lengths = set(outfit_data.get('lengths', []))
        seasonal_lengths = seasonal_specs.get('lengths', set())
        if not outfit_lengths & seasonal_lengths:
            adaptation_results['changes'].append(
                f"Consider using {', '.join(seasonal_lengths)} lengths for {season}"
            )
        
        if adaptation_results['changes']:
            adaptation_results['adapted'] = True
            adaptation_results['suggestions'] = adaptation_results['changes']
        
        return adaptation_results 
