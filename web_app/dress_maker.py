"""
Fashion Outfit Generator with AI-powered outfit generation and image creation.
"""

import os
import asyncio
import requests
import json
import base64
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
import csv
from typing import Dict, List, Set, Optional
import logging
from dataclasses import dataclass
from enum import Enum, auto
import random
import re

# Import the asynchronous client from xAI (or your chosen provider)
from openai import AsyncOpenAI
from openai import OpenAI

# Import prompt management system components
from prompt_manager import PromptManager
from web_app.material_specs import MaterialSpecifications
from web_app.style_context import StyleContext, Style
from web_app.technical_context import TechnicalContext

# Import user profile system components
from web_app.user_profile import (
    UserProfile, Measurements, PhysicalFeatures, StylePreferences,
    MeasurementUnit, StylePreference
)

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


#############################
#      STYLE ANALYSIS       #
#############################

class Style(Enum):
    # Real-world styles
    PROFESSIONAL = auto()
    CASUAL = auto()
    FORMAL = auto()
    ATHLETIC = auto()
    BOHEMIAN = auto()
    MINIMALIST = auto()
    GLAMOROUS = auto()
    EDGY = auto()
    ROMANTIC = auto()
    
    # Character-specific styles
    FANTASY = auto()
    HISTORICAL = auto()
    NOBLE = auto()
    COMMONER = auto()
    COURT = auto()
    ADVENTURE = auto()
    CEREMONIAL = auto()

    # Style Expression Spectrum
    CONSERVATIVE = auto()
    MODERATE = auto()
    BOLD = auto()
    PROVOCATIVE = auto()


@dataclass
class OutfitFeatures:
    colors: Set[str]
    materials: Set[str]
    lengths: Set[str]
    textures: Set[str]
    styles: Set[Style]
    is_character_outfit: bool = False
    character_context: Optional[Dict] = None
    real_world_context: Optional[Dict] = None
    
    # Style Expression Parameters
    modesty_level: int = 5  # 1-10 scale
    provocativeness: int = 5  # 1-10 scale
    elegance_level: int = 5  # 1-10 scale
    sophistication: int = 5  # 1-10 scale
    boldness: int = 5  # 1-10 scale
    subtlety: int = 5  # 1-10 scale
    drama: int = 5  # 1-10 scale
    refinement: int = 5  # 1-10 scale
    
    # Context Parameters
    professionalism: int = 5  # 1-10 scale
    formality: int = 5  # 1-10 scale
    casualness: int = 5  # 1-10 scale
    intimacy: int = 5  # 1-10 scale
    public_presence: int = 5  # 1-10 scale
    private_moments: int = 5  # 1-10 scale
    cultural_context: int = 5  # 1-10 scale
    social_setting: int = 5  # 1-10 scale


class StyleAnalyzer:
    """Analyzes outfit descriptions to determine style categories."""
    def __init__(self):
        self.style_keywords = {
            # Real-world styles
            Style.PROFESSIONAL: {
                'business', 'professional', 'office', 'corporate', 'tailored', 
                'structured', 'executive', 'formal', 'suit', 'blazer', 'power',
                'authoritative', 'polished', 'refined'
            },
            Style.CASUAL: {
                'casual', 'relaxed', 'comfortable', 'everyday', 'laid-back', 
                'easygoing', 'weekend', 'leisure', 'informal', 'sporty',
                'approachable', 'authentic', 'relatable'
            },
            Style.FORMAL: {
                'formal', 'elegant', 'sophisticated', 'luxury', 'black-tie', 
                'gown', 'evening', 'dressy', 'chic', 'refined', 'ceremonial',
                'distinguished', 'regal'
            },
            Style.ATHLETIC: {
                'athletic', 'sporty', 'active', 'workout', 'performance', 
                'gym', 'fitness', 'training', 'sports', 'athleisure',
                'dynamic', 'energetic', 'functional'
            },
            Style.BOHEMIAN: {
                'bohemian', 'boho', 'flowy', 'earthy', 'artistic', 
                'free-spirited', 'hippie', 'eclectic', 'natural', 'organic',
                'wanderer', 'artist', 'unconventional'
            },
            Style.MINIMALIST: {
                'minimalist', 'clean', 'simple', 'modern', 'sleek', 
                'basic', 'understated', 'minimal', 'streamlined', 'essential',
                'zen', 'ascetic', 'purist'
            },
            Style.GLAMOROUS: {
                'glamorous', 'glam', 'luxurious', 'dramatic', 'statement', 
                'bold', 'glitter', 'sparkle', 'shimmer', 'dazzling',
                'diva', 'star', 'celebrity'
            },
            Style.EDGY: {
                'edgy', 'punk', 'rock', 'alternative', 'grunge', 
                'rebellious', 'gothic', 'dark', 'bold', 'unconventional',
                'rebel', 'outlaw', 'anti-hero'
            },
            Style.ROMANTIC: {
                'romantic', 'feminine', 'delicate', 'soft', 'dreamy', 
                'graceful', 'sweet', 'charming', 'lovely', 'whimsical',
                'lover', 'dreamer', 'idealist'
            },
            
            # Character-specific styles
            Style.FANTASY: {
                'fantasy', 'medieval', 'steampunk', 'cyberpunk', 'magical',
                'enchanted', 'mystical', 'otherworldly', 'mythical', 'legendary',
                'spellbound', 'enchanted', 'mystical'
            },
            Style.HISTORICAL: {
                'historical', 'victorian', 'renaissance', 'art deco', '1920s',
                'period', 'era', 'antique', 'vintage', 'classic',
                'time-specific', 'culturally accurate', 'period-appropriate'
            },
            Style.NOBLE: {
                'noble', 'royal', 'aristocratic', 'regal', 'majestic',
                'courtly', 'dignified', 'elegant', 'refined', 'sophisticated',
                'high-born', 'elite', 'privileged'
            },
            Style.COMMONER: {
                'commoner', 'citizen', 'peasant', 'everyday', 'ordinary',
                'simple', 'practical', 'functional', 'basic', 'utilitarian',
                'working-class', 'modest', 'humble'
            },
            Style.COURT: {
                'court', 'ceremonial', 'gala', 'formal', 'official',
                'state', 'diplomatic', 'protocol', 'etiquette', 'tradition',
                'ceremony', 'ritual', 'custom'
            },
            Style.ADVENTURE: {
                'adventure', 'exploration', 'quest', 'journey', 'expedition',
                'travel', 'discovery', 'exploration', 'mission', 'pursuit',
                'practical', 'functional', 'durable'
            },
            Style.CEREMONIAL: {
                'ceremonial', 'ritual', 'sacred', 'holy', 'divine',
                'spiritual', 'religious', 'traditional', 'customary', 'formal',
                'solemn', 'reverent', 'sacred'
            },
            
            # Style Expression Spectrum
            Style.CONSERVATIVE: {
                'conservative', 'modest', 'proper', 'traditional', 'classic',
                'refined', 'sophisticated', 'elegant', 'polished', 'respectable',
                'appropriate', 'suitable', 'dignified', 'proper', 'formal'
            },
            Style.MODERATE: {
                'balanced', 'moderate', 'middle-ground', 'versatile', 'adaptable',
                'flexible', 'practical', 'sensible', 'appropriate', 'suitable',
                'comfortable', 'relaxed', 'easygoing', 'casual', 'smart'
            },
            Style.BOLD: {
                'bold', 'daring', 'statement', 'dramatic', 'striking',
                'eye-catching', 'attention-grabbing', 'unconventional', 'unique',
                'distinctive', 'memorable', 'impactful', 'powerful', 'strong'
            },
            Style.PROVOCATIVE: {
                'provocative', 'seductive', 'alluring', 'sensual', 'tempting',
                'enticing', 'captivating', 'mesmerizing', 'enchanting', 'daring',
                'risqué', 'bold', 'dramatic', 'striking', 'memorable'
            }
        }

        # Style Expression Parameters
        self.expression_parameters = {
            'modesty_level': {
                'high': {'modest', 'conservative', 'proper', 'traditional'},
                'low': {'revealing', 'provocative', 'seductive', 'daring'}
            },
            'provocativeness': {
                'high': {'provocative', 'seductive', 'alluring', 'sensual'},
                'low': {'modest', 'conservative', 'proper', 'traditional'}
            },
            'elegance_level': {
                'high': {'elegant', 'sophisticated', 'refined', 'polished'},
                'low': {'casual', 'relaxed', 'informal', 'simple'}
            },
            'sophistication': {
                'high': {'sophisticated', 'refined', 'elegant', 'polished'},
                'low': {'simple', 'basic', 'plain', 'ordinary'}
            },
            'boldness': {
                'high': {'bold', 'daring', 'dramatic', 'striking'},
                'low': {'subtle', 'understated', 'delicate', 'soft'}
            },
            'subtlety': {
                'high': {'subtle', 'understated', 'delicate', 'soft'},
                'low': {'bold', 'daring', 'dramatic', 'striking'}
            },
            'drama': {
                'high': {'dramatic', 'striking', 'bold', 'daring'},
                'low': {'subtle', 'understated', 'delicate', 'soft'}
            },
            'refinement': {
                'high': {'refined', 'polished', 'elegant', 'sophisticated'},
                'low': {'rough', 'unpolished', 'basic', 'simple'}
            }
        }
        
        # Context Parameters
        self.context_parameters = {
            'professionalism': {
                'high': {'professional', 'business', 'corporate', 'formal'},
                'low': {'casual', 'relaxed', 'informal', 'leisure'}
            },
            'formality': {
                'high': {'formal', 'elegant', 'sophisticated', 'ceremonial'},
                'low': {'casual', 'relaxed', 'informal', 'everyday'}
            },
            'casualness': {
                'high': {'casual', 'relaxed', 'informal', 'everyday'},
                'low': {'formal', 'elegant', 'sophisticated', 'ceremonial'}
            },
            'intimacy': {
                'high': {'intimate', 'private', 'personal', 'close'},
                'low': {'public', 'formal', 'professional', 'distant'}
            },
            'public_presence': {
                'high': {'public', 'formal', 'professional', 'ceremonial'},
                'low': {'private', 'intimate', 'personal', 'casual'}
            },
            'private_moments': {
                'high': {'private', 'intimate', 'personal', 'casual'},
                'low': {'public', 'formal', 'professional', 'ceremonial'}
            },
            'cultural_context': {
                'high': {'cultural', 'traditional', 'authentic', 'period'},
                'low': {'modern', 'contemporary', 'universal', 'global'}
            },
            'social_setting': {
                'high': {'social', 'public', 'formal', 'ceremonial'},
                'low': {'private', 'intimate', 'personal', 'casual'}
            }
        }

    def analyze_description(self, description: str, is_character_outfit: bool = False) -> Set[Style]:
        words = set(description.lower().split())
        styles = set()
        
        # Determine which style categories to check based on outfit type
        style_categories = self.style_keywords.keys()
        if is_character_outfit:
            style_categories = [s for s in style_categories if s in [
                Style.FANTASY, Style.HISTORICAL, Style.NOBLE, Style.COMMONER,
                Style.COURT, Style.ADVENTURE, Style.CEREMONIAL
            ]]
        else:
            style_categories = [s for s in style_categories if s in [
                Style.PROFESSIONAL, Style.CASUAL, Style.FORMAL, Style.ATHLETIC,
                Style.BOHEMIAN, Style.MINIMALIST, Style.GLAMOROUS, Style.EDGY,
                Style.ROMANTIC, Style.CONSERVATIVE, Style.MODERATE, Style.BOLD, Style.PROVOCATIVE
            ]]
        
        for style in style_categories:
            if any(keyword in words for keyword in self.style_keywords[style]):
                styles.add(style)
        
        return styles

    def calculate_expression_parameters(self, description: str) -> Dict[str, int]:
        words = set(description.lower().split())
        parameters = {}
        
        for param, keywords in self.expression_parameters.items():
            score = 5  # Default middle value
            high_matches = len(words & keywords['high'])
            low_matches = len(words & keywords['low'])
            
            if high_matches > low_matches:
                score += min(5, high_matches - low_matches)
            elif low_matches > high_matches:
                score -= min(5, low_matches - high_matches)
            
            parameters[param] = max(1, min(10, score))
        
        return parameters

    def calculate_context_parameters(self, description: str) -> Dict[str, int]:
        words = set(description.lower().split())
        parameters = {}
        
        for param, keywords in self.context_parameters.items():
            score = 5  # Default middle value
            high_matches = len(words & keywords['high'])
            low_matches = len(words & keywords['low'])
            
            if high_matches > low_matches:
                score += min(5, high_matches - low_matches)
            elif low_matches > high_matches:
                score -= min(5, low_matches - high_matches)
            
            parameters[param] = max(1, min(10, score))
        
        return parameters


#############################
#    OUTFIT GENERATOR       #
#############################

class StyleCompatibilityScorer:
    """Scores outfit components for style compatibility."""
    def __init__(self):
        self.style_rules = {
            'PROFESSIONAL': {
                'compatible_with': {'MINIMALIST', 'GLAMOROUS'},
                'incompatible_with': {'BOHEMIAN', 'EDGY'},
                'required_elements': {'structured', 'tailored', 'polished'},
                'forbidden_elements': {'casual', 'distressed', 'oversized'}
            },
            'CASUAL': {
                'compatible_with': {'BOHEMIAN', 'MINIMALIST'},
                'incompatible_with': {'FORMAL', 'GLAMOROUS'},
                'required_elements': {'comfortable', 'relaxed', 'easy'},
                'forbidden_elements': {'formal', 'structured', 'tailored'}
            },
            'FORMAL': {
                'compatible_with': {'GLAMOROUS', 'ROMANTIC'},
                'incompatible_with': {'CASUAL', 'EDGY'},
                'required_elements': {'elegant', 'sophisticated', 'refined'},
                'forbidden_elements': {'casual', 'distressed', 'oversized'}
            },
            'FANTASY': {
                'compatible_with': {'HISTORICAL', 'NOBLE'},
                'incompatible_with': {'PROFESSIONAL', 'CASUAL'},
                'required_elements': {'magical', 'enchanted', 'otherworldly'},
                'forbidden_elements': {'modern', 'casual', 'minimalist'}
            },
            'HISTORICAL': {
                'compatible_with': {'NOBLE', 'COURT'},
                'incompatible_with': {'MODERN', 'FUTURISTIC'},
                'required_elements': {'period-appropriate', 'authentic', 'traditional'},
                'forbidden_elements': {'modern', 'contemporary', 'futuristic'}
            }
        }

    def score_outfit(self, outfit_data: Dict) -> Dict:
        """Scores an outfit for style compatibility."""
        score_results = {
            'compatibility_score': 0,
            'style_violations': [],
            'style_suggestions': [],
            'is_compatible': True
        }

        styles = set(outfit_data.get('features', {}).get('styles', []))
        if not styles:
            score_results['style_violations'].append("No style information available")
            return score_results

        # Get all words from outfit components
        all_text = ' '.join([
            outfit_data.get('components', {}).get(component, '')
            for component in ['top', 'bottom', 'shoes', 'extras']
        ]).lower()

        # Check each style for compatibility
        for style in styles:
            if style not in self.style_rules:
                continue

            rules = self.style_rules[style]
            
            # Check compatible styles
            compatible_styles = styles & rules['compatible_with']
            if compatible_styles:
                score_results['compatibility_score'] += len(compatible_styles) * 10

            # Check incompatible styles
            incompatible_styles = styles & rules['incompatible_with']
            if incompatible_styles:
                score_results['style_violations'].append(
                    f"Style {style} is incompatible with: {', '.join(incompatible_styles)}"
                )
                score_results['compatibility_score'] -= len(incompatible_styles) * 15

            # Check required elements
            missing_required = [
                element for element in rules['required_elements']
                if element not in all_text
            ]
            if missing_required:
                score_results['style_violations'].append(
                    f"Style {style} is missing required elements: {', '.join(missing_required)}"
                )
                score_results['compatibility_score'] -= len(missing_required) * 5
                score_results['style_suggestions'].append(
                    f"Add these elements for better {style} style: {', '.join(missing_required)}"
                )

            # Check forbidden elements
            present_forbidden = [
                element for element in rules['forbidden_elements']
                if element in all_text
            ]
            if present_forbidden:
                score_results['style_violations'].append(
                    f"Style {style} contains forbidden elements: {', '.join(present_forbidden)}"
                )
                score_results['compatibility_score'] -= len(present_forbidden) * 10
                score_results['style_suggestions'].append(
                    f"Remove these elements for better {style} style: {', '.join(present_forbidden)}"
                )

        # Normalize score to 0-100 range
        score_results['compatibility_score'] = max(0, min(100, score_results['compatibility_score']))
        score_results['is_compatible'] = score_results['compatibility_score'] >= 70

        return score_results


class SeasonalAdapter:
    """Adapts outfits for different seasons and weather conditions."""
    def __init__(self):
        self.seasonal_rules = {
            'winter': {
                'materials': {'wool', 'cashmere', 'fleece', 'down', 'faux fur'},
                'layers': {'coat', 'jacket', 'sweater', 'scarf', 'gloves'},
                'colors': {'deep', 'rich', 'dark', 'neutral'},
                'lengths': {'long', 'full-length', 'ankle-length'},
                'temperature_rating': (0, 5)  # 0-5 scale, lower is warmer
            },
            'spring': {
                'materials': {'cotton', 'linen', 'light wool', 'silk'},
                'layers': {'light jacket', 'cardigan', 'shawl'},
                'colors': {'pastel', 'light', 'fresh', 'floral'},
                'lengths': {'midi', 'knee-length', 'three-quarter'},
                'temperature_rating': (4, 7)
            },
            'summer': {
                'materials': {'cotton', 'linen', 'chiffon', 'silk'},
                'layers': {'light', 'minimal'},
                'colors': {'bright', 'light', 'vibrant'},
                'lengths': {'short', 'mini', 'cropped'},
                'temperature_rating': (6, 10)
            },
            'fall': {
                'materials': {'wool', 'tweed', 'corduroy', 'velvet'},
                'layers': {'jacket', 'sweater', 'vest'},
                'colors': {'earthy', 'warm', 'muted'},
                'lengths': {'midi', 'knee-length', 'ankle-length'},
                'temperature_rating': (3, 6)
            }
        }

        self.weather_adaptations = {
            'rain': {
                'additions': {'raincoat', 'umbrella', 'waterproof shoes'},
                'avoid': {'suede', 'silk', 'delicate fabrics'},
                'materials': {'waterproof', 'water-resistant'}
            },
            'snow': {
                'additions': {'winter coat', 'boots', 'hat', 'gloves'},
                'avoid': {'open-toe', 'thin fabrics'},
                'materials': {'insulated', 'waterproof'}
            },
            'wind': {
                'additions': {'windbreaker', 'scarf'},
                'avoid': {'flowy', 'lightweight'},
                'materials': {'wind-resistant'}
            },
            'sun': {
                'additions': {'hat', 'sunglasses'},
                'avoid': {'dark colors', 'heavy fabrics'},
                'materials': {'breathable', 'lightweight'}
            }
        }

    def adapt_outfit(self, outfit_data: Dict, season: str, weather: Optional[str] = None) -> Dict:
        """Adapts an outfit for a specific season and weather condition."""
        adaptation_results = {
            'seasonal_score': 0,
            'adaptations': [],
            'suggestions': [],
            'is_seasonally_appropriate': True
        }

        if season not in self.seasonal_rules:
            adaptation_results['suggestions'].append(f"Unknown season: {season}")
            return adaptation_results

        season_rules = self.seasonal_rules[season]
        features = outfit_data.get('features', {})
        components = outfit_data.get('components', {})

        # Check materials
        materials = set(features.get('materials', []))
        seasonal_materials = materials & season_rules['materials']
        if seasonal_materials:
            adaptation_results['seasonal_score'] += len(seasonal_materials) * 10
        else:
            adaptation_results['suggestions'].append(
                f"Consider adding these season-appropriate materials: {', '.join(season_rules['materials'])}"
            )

        # Check layers
        extras = components.get('extras', '').lower()
        seasonal_layers = any(layer in extras for layer in season_rules['layers'])
        if seasonal_layers:
            adaptation_results['seasonal_score'] += 15
        else:
            adaptation_results['suggestions'].append(
                f"Consider adding these season-appropriate layers: {', '.join(season_rules['layers'])}"
            )

        # Check colors
        colors = set(features.get('colors', []))
        seasonal_colors = any(color in season_rules['colors'] for color in colors)
        if seasonal_colors:
            adaptation_results['seasonal_score'] += 10
        else:
            adaptation_results['suggestions'].append(
                f"Consider using these season-appropriate colors: {', '.join(season_rules['colors'])}"
            )

        # Check lengths
        lengths = set(features.get('lengths', []))
        seasonal_lengths = lengths & season_rules['lengths']
        if seasonal_lengths:
            adaptation_results['seasonal_score'] += 10
        else:
            adaptation_results['suggestions'].append(
                f"Consider these season-appropriate lengths: {', '.join(season_rules['lengths'])}"
            )

        # Apply weather-specific adaptations
        if weather and weather in self.weather_adaptations:
            weather_rules = self.weather_adaptations[weather]
            
            # Check for weather-appropriate additions
            weather_additions = any(addition in extras for addition in weather_rules['additions'])
            if weather_additions:
                adaptation_results['seasonal_score'] += 15
            else:
                adaptation_results['suggestions'].append(
                    f"For {weather} weather, consider adding: {', '.join(weather_rules['additions'])}"
                )

            # Check for materials to avoid
            materials_to_avoid = materials & weather_rules['avoid']
            if materials_to_avoid:
                adaptation_results['suggestions'].append(
                    f"For {weather} weather, avoid these materials: {', '.join(materials_to_avoid)}"
                )
                adaptation_results['seasonal_score'] -= len(materials_to_avoid) * 5

            # Check for weather-appropriate materials
            weather_materials = materials & weather_rules['materials']
            if weather_materials:
                adaptation_results['seasonal_score'] += len(weather_materials) * 10
            else:
                adaptation_results['suggestions'].append(
                    f"For {weather} weather, consider these materials: {', '.join(weather_rules['materials'])}"
                )

        # Normalize score to 0-100 range
        adaptation_results['seasonal_score'] = max(0, min(100, adaptation_results['seasonal_score']))
        adaptation_results['is_seasonally_appropriate'] = adaptation_results['seasonal_score'] >= 70

        return adaptation_results


class OutfitCombinationEngine:
    """Generates and suggests complementary outfit combinations."""
    def __init__(self):
        self.combination_rules = {
            'color_harmony': {
                'analogous': {'max_diff': 30},  # Colors next to each other on color wheel
                'complementary': {'diff': 180},  # Opposite colors
                'triadic': {'diff': 120},  # Three evenly spaced colors
                'monochromatic': {'max_diff': 15}  # Different shades of same color
            },
            'style_transitions': {
                'casual_to_formal': {
                    'steps': ['casual', 'smart casual', 'business casual', 'business', 'formal'],
                    'transition_elements': ['jacket', 'blazer', 'accessories']
                },
                'day_to_night': {
                    'steps': ['day', 'evening', 'night'],
                    'transition_elements': ['jewelry', 'makeup', 'shoes']
                }
            },
            'seasonal_transitions': {
                'summer_to_fall': {
                    'transition_elements': ['layers', 'colors', 'materials'],
                    'suggestions': ['light jacket', 'warmer colors', 'transitional fabrics']
                },
                'winter_to_spring': {
                    'transition_elements': ['layers', 'colors', 'materials'],
                    'suggestions': ['lighter layers', 'brighter colors', 'lighter fabrics']
                }
            }
        }

    def suggest_combinations(self, base_outfit: Dict, num_suggestions: int = 3) -> List[Dict]:
        """Suggests complementary outfit combinations based on a base outfit."""
        suggestions = []
        features = base_outfit.get('features', {})
        styles = set(features.get('styles', []))
        colors = set(features.get('colors', []))
        materials = set(features.get('materials', []))

        # Generate color-based combinations
        color_combinations = self._generate_color_combinations(colors)
        for combo in color_combinations[:num_suggestions]:
            suggestions.append({
                'type': 'color_harmony',
                'base_outfit': base_outfit,
                'suggested_changes': combo,
                'reasoning': f"Creates a {combo['harmony_type']} color scheme"
            })

        # Generate style-based combinations
        style_combinations = self._generate_style_combinations(styles)
        for combo in style_combinations[:num_suggestions]:
            suggestions.append({
                'type': 'style_transition',
                'base_outfit': base_outfit,
                'suggested_changes': combo,
                'reasoning': f"Transitions from {combo['from_style']} to {combo['to_style']}"
            })

        # Generate seasonal combinations
        seasonal_combinations = self._generate_seasonal_combinations(materials)
        for combo in seasonal_combinations[:num_suggestions]:
            suggestions.append({
                'type': 'seasonal_transition',
                'base_outfit': base_outfit,
                'suggested_changes': combo,
                'reasoning': f"Adapts for {combo['season']} weather"
            })

        return suggestions

    def _generate_color_combinations(self, colors: Set[str]) -> List[Dict]:
        """Generates color harmony combinations."""
        combinations = []
        for harmony_type, rules in self.combination_rules['color_harmony'].items():
            # This is a simplified version - in reality, you'd use a color wheel
            # and calculate actual color differences
            suggested_colors = []
            for color in colors:
                if harmony_type == 'monochromatic':
                    suggested_colors.extend([
                        f"lighter {color}",
                        f"darker {color}",
                        f"muted {color}"
                    ])
                elif harmony_type == 'complementary':
                    suggested_colors.append(f"complementary to {color}")
                elif harmony_type == 'analogous':
                    suggested_colors.extend([
                        f"analogous to {color} (lighter)",
                        f"analogous to {color} (darker)"
                    ])
                elif harmony_type == 'triadic':
                    suggested_colors.extend([
                        f"triadic to {color} (first)",
                        f"triadic to {color} (second)"
                    ])
            
            combinations.append({
                'harmony_type': harmony_type,
                'suggested_colors': suggested_colors,
                'changes_needed': ['color adjustments', 'accessory colors']
            })
        
        return combinations

    def _generate_style_combinations(self, styles: Set[str]) -> List[Dict]:
        """Generates style transition combinations."""
        combinations = []
        for transition_type, rules in self.combination_rules['style_transitions'].items():
            steps = rules['steps']
            for i in range(len(steps) - 1):
                if steps[i] in styles:
                    combinations.append({
                        'from_style': steps[i],
                        'to_style': steps[i + 1],
                        'transition_elements': rules['transition_elements'],
                        'changes_needed': [
                            f"add {element}" for element in rules['transition_elements']
                        ]
                    })
        
        return combinations

    def _generate_seasonal_combinations(self, materials: Set[str]) -> List[Dict]:
        """Generates seasonal transition combinations."""
        combinations = []
        for season, rules in self.combination_rules['seasonal_transitions'].items():
            combinations.append({
                'season': season,
                'transition_elements': rules['transition_elements'],
                'suggestions': rules['suggestions'],
                'changes_needed': [
                    f"add {suggestion}" for suggestion in rules['suggestions']
                ]
            })
        
        return combinations


class StyleEvolutionTracker:
    """Tracks and analyzes style evolution over time."""
    def __init__(self):
        self.style_history = []
        self.trend_analysis = {}
        self.evolution_patterns = {}
        self.style_progression = {}
        
    def track_outfit(self, outfit_data: Dict) -> None:
        """Track a new outfit in the style history."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        style_data = {
            'timestamp': timestamp,
            'style_expression': outfit_data.get('style_expression', {}),
            'context_parameters': outfit_data.get('context_parameters', {}),
            'style_compatibility': outfit_data.get('style_compatibility', {}),
            'event': outfit_data.get('event', ''),
            'is_character_outfit': outfit_data.get('is_character_outfit', False)
        }
        self.style_history.append(style_data)
        self._update_trend_analysis(style_data)
        self._update_evolution_patterns(style_data)
        self._update_style_progression(style_data)
        
    def _update_trend_analysis(self, style_data: Dict) -> None:
        """Update trend analysis based on new outfit data."""
        # Analyze style expression trends
        expression = style_data['style_expression']
        if 'overall_style' in expression:
            style = expression['overall_style']
            if style not in self.trend_analysis:
                self.trend_analysis[style] = {'count': 0, 'timestamps': []}
            self.trend_analysis[style]['count'] += 1
            self.trend_analysis[style]['timestamps'].append(style_data['timestamp'])
            
        # Analyze parameter trends
        for param, value in expression.get('parameters', {}).items():
            if param not in self.trend_analysis:
                self.trend_analysis[param] = {'values': [], 'timestamps': []}
            self.trend_analysis[param]['values'].append(value)
            self.trend_analysis[param]['timestamps'].append(style_data['timestamp'])
            
    def _update_evolution_patterns(self, style_data: Dict) -> None:
        """Update evolution patterns based on new outfit data."""
        if len(self.style_history) < 2:
            return
            
        prev_data = self.style_history[-2]
        current_data = style_data
        
        # Track changes in style expression
        prev_style = prev_data['style_expression'].get('overall_style')
        current_style = current_data['style_expression'].get('overall_style')
        
        if prev_style and current_style:
            transition = f"{prev_style}->{current_style}"
            if transition not in self.evolution_patterns:
                self.evolution_patterns[transition] = 0
            self.evolution_patterns[transition] += 1
            
        # Track parameter changes
        for param, current_value in current_data['style_expression'].get('parameters', {}).items():
            prev_value = prev_data['style_expression'].get('parameters', {}).get(param)
            if prev_value is not None:
                change = current_value - prev_value
                if param not in self.evolution_patterns:
                    self.evolution_patterns[param] = {'changes': [], 'timestamps': []}
                self.evolution_patterns[param]['changes'].append(change)
                self.evolution_patterns[param]['timestamps'].append(style_data['timestamp'])
                
    def _update_style_progression(self, style_data: Dict) -> None:
        """Update style progression tracking."""
        if len(self.style_history) < 2:
            return
            
        prev_data = self.style_history[-2]
        current_data = style_data
        
        # Track overall progression
        progression_key = f"{prev_data['event']}->{current_data['event']}"
        if progression_key not in self.style_progression:
            self.style_progression[progression_key] = {
                'count': 0,
                'style_changes': [],
                'parameter_changes': {}
            }
        self.style_progression[progression_key]['count'] += 1
        
        # Track style changes
        prev_style = prev_data['style_expression'].get('overall_style')
        current_style = current_data['style_expression'].get('overall_style')
        if prev_style and current_style:
            self.style_progression[progression_key]['style_changes'].append(
                f"{prev_style}->{current_style}"
            )
            
        # Track parameter changes
        for param, current_value in current_data['style_expression'].get('parameters', {}).items():
            prev_value = prev_data['style_expression'].get('parameters', {}).get(param)
            if prev_value is not None:
                if param not in self.style_progression[progression_key]['parameter_changes']:
                    self.style_progression[progression_key]['parameter_changes'][param] = []
                self.style_progression[progression_key]['parameter_changes'][param].append(
                    current_value - prev_value
                )
                
    def get_evolution_suggestions(self) -> Dict:
        """Generate style evolution suggestions based on tracked data."""
        suggestions = {
            'trend_based': [],
            'pattern_based': [],
            'progression_based': []
        }
        
        # Generate trend-based suggestions
        for style, data in self.trend_analysis.items():
            if isinstance(data, dict) and 'count' in data:
                if data['count'] >= 3:  # Significant trend
                    suggestions['trend_based'].append(
                        f"Consider exploring {style} style more frequently as it's becoming a trend"
                    )
                    
        # Generate pattern-based suggestions
        for transition, data in self.evolution_patterns.items():
            if isinstance(data, int) and data >= 2:  # Common pattern
                if '->' in transition:
                    from_style, to_style = transition.split('->')
                    suggestions['pattern_based'].append(
                        f"Your style often evolves from {from_style} to {to_style}. "
                        f"Consider exploring this transition intentionally"
                    )
                    
        # Generate progression-based suggestions
        for progression, data in self.style_progression.items():
            if isinstance(data, dict) and data.get('count', 0) >= 2:  # Common progression
                event_from, event_to = progression.split('->')
                suggestions['progression_based'].append(
                    f"When transitioning from {event_from} to {event_to}, "
                    f"consider these style changes: {', '.join(set(data.get('style_changes', [])))}"
                )
                
        return suggestions
        
    def get_style_evolution_summary(self) -> Dict:
        """Generate a summary of style evolution."""
        summary = {
            'total_outfits': len(self.style_history),
            'style_distribution': {},
            'parameter_trends': {},
            'evolution_patterns': self.evolution_patterns,
            'style_progression': self.style_progression
        }
        
        # Calculate style distribution
        for data in self.style_history:
            style = data['style_expression'].get('overall_style')
            if style:
                if style not in summary['style_distribution']:
                    summary['style_distribution'][style] = 0
                summary['style_distribution'][style] += 1
                
        # Calculate parameter trends
        for param, data in self.trend_analysis.items():
            if isinstance(data, dict) and 'values' in data:
                values = data['values']
                if values:
                    summary['parameter_trends'][param] = {
                        'average': sum(values) / len(values),
                        'trend': 'increasing' if values[-1] > values[0] else 'decreasing'
                    }
                    
        return summary


class OutfitGenerator:
    """Generates detailed outfit descriptions using an external language model."""
    def __init__(self):
        # Initialize prompt management system
        self.prompt_manager = PromptManager()
        
        # Initialize Ollama URL
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Initialize A/B testing
        self.prompt_counter = 0
        self.prompt_results = {
            'A': {
                'success': 0,
                'total': 0,
                'avg_formality': 0,
                'avg_trendiness': 0,
                'avg_comfort': 0,
                'errors': {
                    'missing_components': 0,
                    'invalid_format': 0,
                    'model_error': 0,
                    'parsing_error': 0,
                    'validation_error': 0
                },
                'error_logs': []
            },
            'B': {
                'success': 0,
                'total': 0,
                'avg_formality': 0,
                'avg_trendiness': 0,
                'avg_comfort': 0,
                'errors': {
                    'missing_components': 0,
                    'invalid_format': 0,
                    'model_error': 0,
                    'parsing_error': 0,
                    'validation_error': 0
                },
                'error_logs': []
            }
        }
        
        # Initialize user profile system
        self.user_profile = UserProfile()
        
        # Initialize other components
        self.style_analyzer = StyleAnalyzer()
        self.style_scorer = StyleCompatibilityScorer()
        self.seasonal_adapter = SeasonalAdapter()
        self.outfit_combiner = OutfitCombinationEngine()
        self.style_tracker = StyleEvolutionTracker()
        self.cultural_validator = CulturalValidator()
        
        # Initialize catalog
        self.catalog_file = "outfit_catalog.csv"
        self.initialize_catalog()
        
        # Initialize creative components
        self.creative_components = {
            'style': {
                'classic': ['timeless', 'elegant', 'sophisticated'],
                'modern': ['contemporary', 'minimalist', 'clean'],
                'bohemian': ['free-spirited', 'artistic', 'eclectic'],
                'romantic': ['feminine', 'delicate', 'soft'],
                'edgy': ['bold', 'daring', 'unconventional'],
                'sporty': ['athletic', 'casual', 'dynamic'],
                'luxury': ['opulent', 'refined', 'premium'],
                'vintage': ['retro', 'nostalgic', 'classic'],
                'avant-garde': ['experimental', 'innovative', 'artistic'],
                'minimalist': ['simple', 'clean', 'essential']
            },
            'color': {
                'classic': ['black', 'white', 'navy', 'gray', 'beige'],
                'bold': ['red', 'purple', 'emerald', 'gold', 'cobalt'],
                'soft': ['pastel pink', 'lavender', 'mint', 'peach', 'sky blue'],
                'earthy': ['olive', 'terracotta', 'sage', 'mustard', 'rust'],
                'monochrome': ['black', 'white', 'gray', 'ivory', 'charcoal'],
                'jewel': ['ruby', 'sapphire', 'emerald', 'amethyst', 'topaz'],
                'neutral': ['cream', 'taupe', 'camel', 'khaki', 'mushroom'],
                'vibrant': ['fuchsia', 'turquoise', 'coral', 'lime', 'electric blue'],
                'muted': ['dusty rose', 'sage green', 'mauve', 'slate', 'moss'],
                'metallic': ['silver', 'gold', 'bronze', 'copper', 'platinum']
            },
            'material': {
                'luxury': ['silk', 'cashmere', 'velvet', 'leather', 'satin'],
                'casual': ['cotton', 'denim', 'linen', 'knit', 'canvas'],
                'formal': ['wool', 'tweed', 'silk', 'crepe', 'gabardine'],
                'summer': ['linen', 'cotton', 'seersucker', 'chambray', 'voile'],
                'winter': ['wool', 'cashmere', 'fleece', 'flannel', 'tweed'],
                'spring': ['cotton', 'linen', 'silk', 'chiffon', 'poplin'],
                'fall': ['tweed', 'corduroy', 'flannel', 'wool', 'velvet']
            },
            'silhouette': {
                'fitted': ['bodycon', 'tailored', 'structured'],
                'flowing': ['a-line', 'empire', 'balloon'],
                'relaxed': ['oversized', 'loose', 'comfortable'],
                'dramatic': ['voluminous', 'exaggerated', 'statement'],
                'minimal': ['straight', 'simple', 'clean'],
                'feminine': ['flared', 'ruffled', 'draped'],
                'masculine': ['boxy', 'angular', 'sharp']
            },
            'accessory': {
                'minimal': ['simple necklace', 'stud earrings', 'thin bracelet', 'delicate watch'],
                'statement': ['bold necklace', 'chandelier earrings', 'chunky bracelet', 'statement ring'],
                'classic': ['pearl necklace', 'diamond studs', 'gold bracelet', 'leather watch'],
                'bohemian': ['layered necklaces', 'feather earrings', 'beaded bracelet', 'anklet'],
                'luxury': ['diamond necklace', 'gold earrings', 'luxury watch', 'designer bag'],
                'casual': ['leather bracelet', 'simple hoop earrings', 'canvas bag', 'sports watch'],
                'vintage': ['antique brooch', 'vintage watch', 'retro sunglasses', 'classic bag']
            },
            'event': {
                'cocktail': {
                    'formality': 'semi-formal',
                    'mood': 'elegant',
                    'key_elements': ['statement pieces', 'luxury fabrics', 'sophisticated accessories']
                },
                'casual': {
                    'formality': 'casual',
                    'mood': 'relaxed',
                    'key_elements': ['comfortable fabrics', 'practical accessories', 'easy styling']
                },
                'formal': {
                    'formality': 'formal',
                    'mood': 'sophisticated',
                    'key_elements': ['luxury materials', 'refined details', 'elegant accessories']
                },
                'business': {
                    'formality': 'professional',
                    'mood': 'polished',
                    'key_elements': ['structured pieces', 'neutral colors', 'minimal accessories']
                },
                'party': {
                    'formality': 'festive',
                    'mood': 'playful',
                    'key_elements': ['bold colors', 'statement pieces', 'fun accessories']
                }
            },
            'season': {
                'spring': {
                    'colors': ['pastel', 'fresh', 'light'],
                    'materials': ['lightweight', 'breathable'],
                    'mood': ['fresh', 'renewal']
                },
                'summer': {
                    'colors': ['bright', 'vibrant', 'light'],
                    'materials': ['light', 'airy'],
                    'mood': ['carefree', 'sunny']
                },
                'fall': {
                    'colors': ['rich', 'earthy', 'warm'],
                    'materials': ['medium weight', 'textured'],
                    'mood': ['cozy', 'transitional']
                },
                'winter': {
                    'colors': ['deep', 'rich', 'dark'],
                    'materials': ['heavy', 'warm'],
                    'mood': ['elegant', 'cozy']
                }
            },
            'tops': {
                'formal': ['blouse', 'button-up shirt', 'silk top', 'structured blouse', 'tailored shirt'],
                'casual': ['t-shirt', 'tank top', 'sweater', 'hoodie', 'crop top'],
                'luxury': ['silk blouse', 'cashmere sweater', 'designer top', 'luxury knit', 'premium blouse'],
                'business': ['button-up shirt', 'blouse', 'polo shirt', 'turtleneck', 'sweater'],
                'party': ['sequin top', 'crop top', 'statement blouse', 'glamorous top', 'dressy blouse'],
                'summer': ['tank top', 'sleeveless blouse', 'light sweater', 'crop top', 'summer blouse'],
                'winter': ['sweater', 'turtleneck', 'long sleeve top', 'thermal top', 'winter blouse']
            },
            'bottoms': {
                'formal': ['trousers', 'pencil skirt', 'tailored pants', 'formal skirt', 'dress pants'],
                'casual': ['jeans', 'shorts', 'leggings', 'casual pants', 'skirt'],
                'luxury': ['designer pants', 'luxury skirt', 'premium jeans', 'tailored shorts', 'high-end leggings'],
                'business': ['slacks', 'pencil skirt', 'dress pants', 'tailored shorts', 'business skirt'],
                'party': ['sequin pants', 'party skirt', 'dressy shorts', 'glamorous pants', 'evening skirt'],
                'summer': ['shorts', 'skirt', 'light pants', 'summer jeans', 'casual shorts'],
                'winter': ['pants', 'jeans', 'leggings', 'winter skirt', 'thermal leggings']
            },
            'shoes': {
                'formal': ['heels', 'pumps', 'dress shoes', 'formal flats', 'elegant sandals'],
                'casual': ['sneakers', 'flats', 'sandals', 'loafers', 'casual boots'],
                'luxury': ['designer heels', 'luxury flats', 'premium boots', 'high-end sneakers', 'elegant sandals'],
                'business': ['pumps', 'loafers', 'dress shoes', 'business flats', 'professional heels'],
                'party': ['heels', 'party shoes', 'glamorous sandals', 'evening shoes', 'statement boots'],
                'summer': ['sandals', 'flats', 'summer shoes', 'casual sneakers', 'light boots'],
                'winter': ['boots', 'winter shoes', 'closed-toe heels', 'warm flats', 'winter sneakers']
            },
            'outerwear': {
                'formal': ['blazer', 'coat', 'jacket', 'formal cardigan', 'structured wrap'],
                'casual': ['jacket', 'sweater', 'hoodie', 'cardigan', 'casual coat'],
                'luxury': ['designer coat', 'luxury jacket', 'premium blazer', 'high-end wrap', 'elegant cardigan'],
                'business': ['blazer', 'coat', 'jacket', 'cardigan', 'professional wrap'],
                'party': ['evening wrap', 'party jacket', 'glamorous coat', 'statement blazer', 'dressy cardigan'],
                'summer': ['light jacket', 'cardigan', 'summer wrap', 'casual blazer', 'light coat'],
                'winter': ['coat', 'jacket', 'winter wrap', 'warm cardigan', 'thermal blazer']
            },
            'accessories': {
                'formal': ['necklace', 'earrings', 'watch', 'belt', 'scarf'],
                'casual': ['bracelet', 'necklace', 'watch', 'belt', 'sunglasses'],
                'luxury': ['designer bag', 'luxury watch', 'premium jewelry', 'high-end scarf', 'elegant belt'],
                'business': ['watch', 'necklace', 'belt', 'professional bag', 'minimal jewelry'],
                'party': ['statement jewelry', 'evening bag', 'glamorous accessories', 'party belt', 'dressy scarf'],
                'summer': ['sunglasses', 'summer bag', 'light jewelry', 'casual belt', 'summer scarf'],
                'winter': ['winter scarf', 'gloves', 'warm accessories', 'winter bag', 'seasonal jewelry']
            },
            'extras': {
                'formal': ['gloves', 'hat', 'stockings', 'formal bag', 'elegant umbrella'],
                'casual': ['backpack', 'hat', 'socks', 'casual bag', 'umbrella'],
                'luxury': ['designer bag', 'luxury hat', 'premium gloves', 'high-end umbrella', 'elegant stockings'],
                'business': ['briefcase', 'umbrella', 'professional bag', 'business hat', 'formal gloves'],
                'party': ['evening bag', 'party hat', 'glamorous gloves', 'statement umbrella', 'dressy stockings'],
                'summer': ['summer hat', 'sunglasses', 'light bag', 'casual umbrella', 'summer gloves'],
                'winter': ['winter hat', 'gloves', 'warm stockings', 'winter bag', 'seasonal umbrella']
            }
        }
        
        # Initialize outfit themes
        self.outfit_themes = {
            'color_palettes': {
                'classic': ['black', 'white', 'navy', 'gray', 'beige'],
                'bold': ['red', 'purple', 'emerald', 'gold', 'cobalt'],
                'soft': ['pastel pink', 'lavender', 'mint', 'peach', 'sky blue'],
                'earthy': ['olive', 'terracotta', 'sage', 'mustard', 'rust'],
                'monochrome': ['black', 'white', 'gray', 'ivory', 'charcoal'],
                'jewel': ['ruby', 'sapphire', 'emerald', 'amethyst', 'topaz'],
                'neutral': ['cream', 'taupe', 'camel', 'khaki', 'mushroom'],
                'vibrant': ['fuchsia', 'turquoise', 'coral', 'lime', 'electric blue'],
                'muted': ['dusty rose', 'sage green', 'mauve', 'slate', 'moss'],
                'metallic': ['silver', 'gold', 'bronze', 'copper', 'platinum']
            },
            'style_themes': {
                'classic': ['timeless', 'elegant', 'sophisticated'],
                'modern': ['contemporary', 'minimalist', 'clean'],
                'bohemian': ['free-spirited', 'artistic', 'eclectic'],
                'romantic': ['feminine', 'delicate', 'soft'],
                'edgy': ['bold', 'daring', 'unconventional'],
                'sporty': ['athletic', 'casual', 'dynamic'],
                'luxury': ['opulent', 'refined', 'premium'],
                'vintage': ['retro', 'nostalgic', 'classic'],
                'avant-garde': ['experimental', 'innovative', 'artistic'],
                'minimalist': ['simple', 'clean', 'essential']
            },
            'style_mixes': {
                'classic_modern': {
                    'primary': 'classic',
                    'secondary': 'modern',
                    'description': 'A sophisticated blend of timeless elegance with contemporary touches',
                    'elements': ['structured silhouettes', 'clean lines', 'luxury fabrics', 'minimal accessories']
                },
                'bohemian_luxury': {
                    'primary': 'bohemian',
                    'secondary': 'luxury',
                    'description': 'Free-spirited style elevated with premium materials and refined details',
                    'elements': ['flowing fabrics', 'rich textures', 'artistic patterns', 'statement pieces']
                },
                'romantic_edgy': {
                    'primary': 'romantic',
                    'secondary': 'edgy',
                    'description': 'Delicate femininity with bold, unconventional elements',
                    'elements': ['soft fabrics', 'dramatic details', 'contrasting textures', 'bold accessories']
                },
                'minimalist_luxury': {
                    'primary': 'minimalist',
                    'secondary': 'luxury',
                    'description': 'Understated elegance with premium materials and impeccable tailoring',
                    'elements': ['clean lines', 'quality fabrics', 'subtle details', 'refined accessories']
                },
                'vintage_modern': {
                    'primary': 'vintage',
                    'secondary': 'modern',
                    'description': 'Nostalgic charm updated with contemporary styling',
                    'elements': ['retro silhouettes', 'modern fabrics', 'classic patterns', 'updated accessories']
                },
                'sporty_luxury': {
                    'primary': 'sporty',
                    'secondary': 'luxury',
                    'description': 'Athletic elements elevated with premium materials and sophisticated details',
                    'elements': ['dynamic shapes', 'luxury fabrics', 'technical details', 'refined accessories']
                },
                'avant-garde_classic': {
                    'primary': 'avant-garde',
                    'secondary': 'classic',
                    'description': 'Innovative design grounded in timeless elegance',
                    'elements': ['experimental shapes', 'traditional fabrics', 'artistic details', 'classic accessories']
                },
                'romantic_minimalist': {
                    'primary': 'romantic',
                    'secondary': 'minimalist',
                    'description': 'Delicate femininity with clean, essential elements',
                    'elements': ['soft fabrics', 'simple lines', 'subtle details', 'minimal accessories']
                },
                'edgy_luxury': {
                    'primary': 'edgy',
                    'secondary': 'luxury',
                    'description': 'Bold, unconventional style with premium materials and refined execution',
                    'elements': ['dramatic shapes', 'luxury fabrics', 'bold details', 'statement accessories']
                },
                'bohemian_minimalist': {
                    'primary': 'bohemian',
                    'secondary': 'minimalist',
                    'description': 'Free-spirited style with clean, essential elements',
                    'elements': ['natural fabrics', 'simple lines', 'artistic details', 'minimal accessories']
                }
            },
            'material_themes': {
                'luxury': ['silk', 'cashmere', 'velvet', 'leather', 'satin'],
                'casual': ['cotton', 'denim', 'linen', 'knit', 'canvas'],
                'formal': ['wool', 'tweed', 'silk', 'crepe', 'gabardine'],
                'summer': ['linen', 'cotton', 'seersucker', 'chambray', 'voile'],
                'winter': ['wool', 'cashmere', 'fleece', 'flannel', 'tweed'],
                'spring': ['cotton', 'linen', 'silk', 'chiffon', 'poplin'],
                'fall': ['tweed', 'corduroy', 'flannel', 'wool', 'velvet']
            },
            'material_combinations': {
                'luxury_casual': {
                    'primary': 'luxury',
                    'secondary': 'casual',
                    'description': 'Premium materials with relaxed styling',
                    'elements': ['silk', 'cashmere', 'cotton', 'linen', 'leather']
                },
                'formal_casual': {
                    'primary': 'formal',
                    'secondary': 'casual',
                    'description': 'Structured materials with comfortable elements',
                    'elements': ['wool', 'cotton', 'tweed', 'denim', 'linen']
                },
                'seasonal_luxury': {
                    'primary': 'luxury',
                    'secondary': 'seasonal',
                    'description': 'Premium materials adapted for the season',
                    'elements': ['silk', 'cashmere', 'wool', 'linen', 'cotton']
                },
                'textural_mix': {
                    'primary': 'textural',
                    'secondary': 'mixed',
                    'description': 'Rich combination of different textures',
                    'elements': ['velvet', 'silk', 'leather', 'knit', 'tweed']
                },
                'light_layered': {
                    'primary': 'light',
                    'secondary': 'layered',
                    'description': 'Lightweight materials in layered combinations',
                    'elements': ['chiffon', 'silk', 'cotton', 'linen', 'voile']
                }
            },
            'silhouette_themes': {
                'fitted': ['bodycon', 'tailored', 'structured'],
                'flowing': ['a-line', 'empire', 'balloon'],
                'relaxed': ['oversized', 'loose', 'comfortable'],
                'dramatic': ['voluminous', 'exaggerated', 'statement'],
                'minimal': ['straight', 'simple', 'clean'],
                'feminine': ['flared', 'ruffled', 'draped'],
                'masculine': ['boxy', 'angular', 'sharp']
            }
        }
        
        # Initialize keyword sets
        self.color_keywords = {
            'black', 'white', 'red', 'blue', 'green', 'yellow', 'purple',
            'pink', 'orange', 'brown', 'gray', 'navy', 'beige', 'cream',
            'gold', 'silver', 'bronze', 'burgundy', 'teal', 'mint'
        }
        
        self.material_keywords = {
            'cotton', 'silk', 'wool', 'linen', 'denim', 'leather', 'suede',
            'cashmere', 'velvet', 'lace', 'satin', 'polyester', 'nylon',
            'spandex', 'rayon', 'tweed', 'corduroy', 'knit', 'fleece'
        }
        
        self.length_keywords = {
            'short', 'medium', 'long', 'mini', 'maxi', 'midi', 'ankle',
            'knee', 'calf', 'floor', 'cropped', 'full', 'three-quarter'
        }
        
        self.texture_keywords = {
            'smooth', 'rough', 'soft', 'hard', 'shiny', 'matte', 'glossy',
            'textured', 'patterned', 'solid', 'sheer', 'opaque', 'transparent'
        }

    def _get_ab_prompt(self, event: str, creative_direction: Dict, user_guidance: Optional[Dict] = None,
                      character_context: Optional[Dict] = None, real_world_context: Optional[Dict] = None,
                      style_expression: Optional[str] = None) -> str:
        """Get either A or B prompt based on counter."""
        self.prompt_counter += 1
        use_b = self.prompt_counter % 2 == 0
        
        if use_b:
            return self._generate_xml_prompt(event, creative_direction, user_guidance,
                                          character_context, real_world_context, style_expression)
        else:
            return self._generate_standard_prompt(event, creative_direction, user_guidance,
                                                character_context, real_world_context, style_expression)
    
    def _generate_xml_prompt(self, event: str, creative_direction: Dict, user_guidance: Optional[Dict] = None,
                           character_context: Optional[Dict] = None, real_world_context: Optional[Dict] = None,
                           style_expression: Optional[str] = None) -> str:
        """Generate an XML-based prompt for outfit generation."""
        prompt = f"""<outfit_request>
    <event_type>{event}</event_type>
    <style>
        <direction>{creative_direction['style']['description']}</direction>
        <colors>{creative_direction['color']['description']}</colors>
        <materials>{creative_direction['material']['description']}</materials>
        <silhouette>{creative_direction['silhouette']['description']}</silhouette>
    </style>
    <required_components>
        <top>
            <description>Describe a specific top with style, material, and color</description>
            <format>blouse, shirt, etc.</format>
        </top>
        <bottom>
            <description>Describe a specific bottom with style, material, and color</description>
            <format>pants, skirt, etc.</format>
        </bottom>
        <shoes>
            <description>Describe specific shoes with style, material, and color</description>
            <format>heels, flats, etc.</format>
        </shoes>
        <extras>
            <description>Describe any additional accessories or outerwear</description>
            <format>optional</format>
        </extras>
    </required_components>"""

        if user_guidance:
            prompt += f"""
    <user_preferences>
        <primary_style>{user_guidance.get('primary_style', '')}</primary_style>
        <favorite_colors>{', '.join(user_guidance.get('favorite_colors', []))}</favorite_colors>
        <favorite_materials>{', '.join(user_guidance.get('favorite_materials', []))}</favorite_materials>
        <style_adaptability>{user_guidance.get('style_adaptability', 5)}</style_adaptability>
        <comfort_priority>{user_guidance.get('comfort_priority', 5)}</comfort_priority>
        <modesty_level>{user_guidance.get('modesty_level', 5)}</modesty_level>
    </user_preferences>"""

        if character_context:
            prompt += f"""
    <character_context>
        <type>{character_context.get('type', 'unknown')}</type>
        <background>{character_context.get('background', 'unknown')}</background>
        <personality>{character_context.get('personality', 'unknown')}</personality>
    </character_context>"""

        if real_world_context:
            prompt += f"""
    <real_world_context>
        <location>{real_world_context.get('location', 'unknown')}</location>
        <time_period>{real_world_context.get('time_period', 'unknown')}</time_period>
        <cultural_context>{real_world_context.get('cultural_context', 'unknown')}</cultural_context>
    </real_world_context>"""

        if style_expression:
            prompt += f"""
    <style_expression>{style_expression}</style_expression>"""

        prompt += """
    <instructions>
        <format>Provide a complete, specific outfit description with all required components</format>
        <style>Clear and decisive, no questions or options</style>
        <output>Structured text description of one definitive outfit</output>
    </instructions>
</outfit_request>"""

        return prompt
    
    def _generate_standard_prompt(self, event: str, creative_direction: Dict, user_guidance: Optional[Dict] = None,
                                character_context: Optional[Dict] = None, real_world_context: Optional[Dict] = None,
                                style_expression: Optional[str] = None) -> str:
        """Generate the standard prompt (existing system)."""
        # Base prompt
        prompt = f"""Describe a complete outfit in text format for a {event} event. 
The outfit must be described in a clear, decisive manner with specific components.
Do not ask questions or provide options - instead, describe a complete, specific outfit.

Required components to describe:
1. Top: Describe a specific top (blouse, shirt, etc.) with its style, material, and color
2. Bottom: Describe a specific bottom (pants, skirt, etc.) with its style, material, and color
3. Shoes: Describe specific shoes with their style, material, and color
4. Extras: Describe any additional accessories or outerwear

Format the response as a clear, structured description with these exact components.
Do not include questions or multiple options - provide one specific, complete outfit description.

Style direction: {creative_direction['style']['description']}
Color palette: {creative_direction['color']['description']}
Material focus: {creative_direction['material']['description']}
Silhouette: {creative_direction['silhouette']['description']}
"""

        # Add user-specific guidance if available
        if user_guidance:
            prompt += f"\nUser style preferences:\n"
            prompt += f"Primary style: {user_guidance.get('primary_style', '')}\n"
            prompt += f"Favorite colors: {', '.join(user_guidance.get('favorite_colors', []))}\n"
            prompt += f"Favorite materials: {', '.join(user_guidance.get('favorite_materials', []))}\n"
            prompt += f"Style adaptability: {user_guidance.get('style_adaptability', 5)}/10\n"
            prompt += f"Comfort priority: {user_guidance.get('comfort_priority', 5)}/10\n"
            prompt += f"Modesty level: {user_guidance.get('modesty_level', 5)}/10\n"

        # Add character context if applicable
        if character_context:
            prompt += f"\nCharacter context:\n"
            prompt += f"Character type: {character_context.get('type', 'unknown')}\n"
            prompt += f"Character background: {character_context.get('background', 'unknown')}\n"
            prompt += f"Character personality: {character_context.get('personality', 'unknown')}\n"

        # Add real-world context if available
        if real_world_context:
            prompt += f"\nReal-world context:\n"
            prompt += f"Location: {real_world_context.get('location', 'unknown')}\n"
            prompt += f"Time period: {real_world_context.get('time_period', 'unknown')}\n"
            prompt += f"Cultural context: {real_world_context.get('cultural_context', 'unknown')}\n"

        # Add style expression if specified
        if style_expression:
            prompt += f"\nStyle expression: {style_expression}\n"

        # Final instruction
        prompt += "\nProvide a complete, specific outfit description with all required components. Do not ask questions or provide options - describe one definitive outfit."

        return prompt
    
    def generate_outfit_prompt(self, event: str, outfit_number: int, variation: int,
                             is_character_outfit: bool = False,
                             character_context: Optional[Dict] = None,
                             real_world_context: Optional[Dict] = None,
                             style_expression: Optional[str] = None,
                             user_name: Optional[str] = None) -> str:
        """Generate a prompt for outfit generation."""
        # Get creative direction
        creative_direction = self._get_creative_direction(variation)
        
        # Get user guidance if available
        user_guidance = None
        if user_name:
            user_guidance = self.user_profile.get_style_guidance(user_name)
        
        # Get A/B prompt
        prompt = self._get_ab_prompt(event, creative_direction, user_guidance,
                                   character_context, real_world_context, style_expression)
        
        return prompt
    
    def _update_ab_results(self, prompt_type: str, success: bool, formality: int, trendiness: int, comfort: int):
        """Update A/B testing results."""
        results = self.prompt_results[prompt_type]
        results['total'] += 1
        if success:
            results['success'] += 1
        
        # Update averages
        results['avg_formality'] = ((results['avg_formality'] * (results['total'] - 1)) + formality) / results['total']
        results['avg_trendiness'] = ((results['avg_trendiness'] * (results['total'] - 1)) + trendiness) / results['total']
        results['avg_comfort'] = ((results['avg_comfort'] * (results['total'] - 1)) + comfort) / results['total']
    
    def get_ab_results(self) -> Dict:
        """Get current A/B testing results."""
        return {
            'A': {
                'success_rate': self.prompt_results['A']['success'] / self.prompt_results['A']['total'] if self.prompt_results['A']['total'] > 0 else 0,
                'avg_formality': self.prompt_results['A']['avg_formality'],
                'avg_trendiness': self.prompt_results['A']['avg_trendiness'],
                'avg_comfort': self.prompt_results['A']['avg_comfort'],
                'error_rates': {
                    error_type: count / self.prompt_results['A']['total'] if self.prompt_results['A']['total'] > 0 else 0
                    for error_type, count in self.prompt_results['A']['errors'].items()
                },
                'total_errors': sum(self.prompt_results['A']['errors'].values())
            },
            'B': {
                'success_rate': self.prompt_results['B']['success'] / self.prompt_results['B']['total'] if self.prompt_results['B']['total'] > 0 else 0,
                'avg_formality': self.prompt_results['B']['avg_formality'],
                'avg_trendiness': self.prompt_results['B']['avg_trendiness'],
                'avg_comfort': self.prompt_results['B']['avg_comfort'],
                'error_rates': {
                    error_type: count / self.prompt_results['B']['total'] if self.prompt_results['B']['total'] > 0 else 0
                    for error_type, count in self.prompt_results['B']['errors'].items()
                },
                'total_errors': sum(self.prompt_results['B']['errors'].values())
            }
        }
    
    def get_error_logs(self, prompt_type: str, limit: int = 10) -> List[Dict]:
        """Get recent error logs for a prompt type."""
        return self.prompt_results[prompt_type]['error_logs'][-limit:]
    
    def clear_error_logs(self, prompt_type: str):
        """Clear error logs for a prompt type."""
        self.prompt_results[prompt_type]['error_logs'] = []

    def generate_outfit(self, event: str, num_outfits: int, variations_per_outfit: int,
                       is_character_outfit: bool = False,
                       character_context: Optional[Dict] = None,
                       real_world_context: Optional[Dict] = None,
                       style_expression: Optional[str] = None,
                       user_name: Optional[str] = None,
                       max_retries: int = 3) -> List[Dict]:
        """Generate outfits with retry logic for missing components."""
        outfits = []
        
        for i in range(num_outfits):
            for j in range(variations_per_outfit):
                retries = 0
                while retries < max_retries:
                    # Generate the initial outfit
                    prompt = self.generate_outfit_prompt(
                        event, i + 1, j + 1,
                        is_character_outfit,
                        character_context,
                        real_world_context,
                        style_expression,
                        user_name
                    )
                    
                    response = self._generate_with_language_model(prompt)
                    outfit_data = self.parse_outfit_response(response)
                    
                    # Add outfit ID and metadata
                    outfit_id = f"outfit_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}_{j}"
                    outfit_data['outfit_id'] = outfit_id
                    outfit_data['event'] = event
                    outfit_data['created_at'] = datetime.now().isoformat()
                    
                    # Check if any required components are missing
                    missing_components = []
                    for component in ['top', 'bottom', 'shoes']:
                        if not outfit_data.get(component):
                            missing_components.append(component)
                    
                    if not missing_components:
                        # All components present, validate and add to outfits
                        if self._validate_outfit_data(outfit_data):
                            outfits.append(outfit_data)
                            break
                    
                    # Try to generate missing components
                    for component in missing_components:
                        logger.info(f"Attempting to generate missing {component}")
                        generated_component = self._generate_missing_component(component, outfit_data)
                        if generated_component and not generated_component.startswith("Please provide"):
                            outfit_data[component] = generated_component
                        else:
                            logger.error(f"Failed to generate valid {component}")
                            break
                    
                    retries += 1
                
                if retries == max_retries:
                    logger.error(f"Failed to generate valid outfit after {max_retries} attempts")
        
        return outfits
    
    def _generate_missing_component(self, component: str, existing_outfit: Dict) -> str:
        """Generate a missing component based on the existing outfit."""
        prompt = f"Based on this outfit, generate a matching {component}:\n\n"
        
        if existing_outfit.get('top') and component != 'top':
            prompt += f"Top: {existing_outfit['top']}\n"
        if existing_outfit.get('bottom') and component != 'bottom':
            prompt += f"Bottom: {existing_outfit['bottom']}\n"
        if existing_outfit.get('shoes') and component != 'shoes':
            prompt += f"Shoes: {existing_outfit['shoes']}\n"
        
        prompt += f"\nFormality: {existing_outfit.get('formality', 5)}/10\n"
        prompt += f"Style: {', '.join(str(s) for s in existing_outfit.get('styles', []))}\n"
        prompt += f"Colors: {', '.join(existing_outfit.get('colors', []))}\n"
        prompt += f"Materials: {', '.join(existing_outfit.get('materials', []))}\n"
        
        prompt += f"\nPlease generate a {component} that matches this outfit. Format as '**{component.title()}:** <description>'"
        
        response = self._generate_with_language_model(prompt)
        return response.strip()
    
    def _validate_outfit_data(self, outfit_data: Dict) -> bool:
        """Validate the outfit data has all required components."""
        required_components = ['top', 'bottom', 'shoes']
        required_fields = ['outfit_id', 'event', 'created_at']
        
        # Check required components
        for component in required_components:
            if not outfit_data.get(component):
                logger.error(f"Missing required component: {component}")
                return False
        
        # Check required fields
        for field in required_fields:
            if not outfit_data.get(field):
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate component content
        for component in required_components:
            content = outfit_data.get(component, '')
            if not content or content.startswith("Please provide"):
                logger.error(f"Invalid {component} content")
                return False
        
        return True

    def _prepare_format_data(self, outfit_data: Dict) -> Dict:
        """Prepare data for template formatting with enhanced material and style details."""
        features = outfit_data.get('features', {})
        components = outfit_data.get('components', {})
        
        # Get material specifications
        materials = features.get('materials', [])
        material_details = []
        for material in materials:
            material_props = self.material_specs.get_material_properties(material)
            material_details.append(f"{material}: {', '.join(material_props.get('properties', []))}")
        
        # Get texture specifications
        textures = features.get('textures', [])
        texture_details = []
        for texture in textures:
            texture_props = self.material_specs.get_texture_properties(texture)
            texture_details.append(f"{texture}: {', '.join(texture_props.get('visual_properties', []))}")
        
        # Get style specifications
        styles = features.get('styles', [])
        style_details = []
        for style in styles:
            style_props = self.style_context.get_style_keywords(style)
            style_details.append(f"{style.value}: {', '.join(style_props.get('keywords', []))}")
        
        return {
            'lighting_setup': 'three-point lighting with soft box and rim light',
            'camera_angle': 'three-quarter view',
            'depth_of_field': 'shallow to medium',
            'color_grading': 'high fashion editorial',
            'resolution': 'high resolution',
            'top_description': components.get('top', ''),
            'bottom_description': components.get('bottom', ''),
            'top_material': materials[0] if materials else '',
            'bottom_material': materials[-1] if materials else '',
            'texture_description': textures[0] if textures else '',
            'construction_details': 'premium construction with attention to detail',
            'specific_features': 'designer details and premium finishes',
            'bottom_texture': textures[-1] if textures else '',
            'cut_description': 'tailored fit',
            'bottom_features': 'premium construction details',
            'accessories_list': components.get('extras', ''),
            'accessory_materials': materials[0] if materials else '',
            'accessory_placement': 'strategically positioned',
            'primary_materials': ', '.join(material_details),
            'texture_details': ', '.join(texture_details),
            'surface_properties': 'premium finish',
            'material_light_behavior': 'luxurious light interaction',
            'seam_specifications': 'premium construction',
            'draping_behavior': 'elegant drape',
            'material_movement': 'fluid movement',
            'style_details': ', '.join(style_details)
        }

    def _get_creative_direction(self, variation: int) -> Dict:
        """Get creative direction for outfit generation."""
        # Get random selections from each category
        style = random.choice(list(self.creative_components['style'].keys()))
        color = random.choice(list(self.creative_components['color'].keys()))
        material = random.choice(list(self.creative_components['material'].keys()))
        silhouette = random.choice(list(self.creative_components['silhouette'].keys()))
        
        # Get the specific elements for each category
        style_elements = self.creative_components['style'][style]
        color_elements = self.creative_components['color'][color]
        material_elements = self.creative_components['material'][material]
        silhouette_elements = self.creative_components['silhouette'][silhouette]
        
        # Create the creative direction dictionary
        creative_direction = {
            'style': {
                'name': style,
                'elements': style_elements,
                'description': f"A {style} style with {', '.join(style_elements)} elements"
            },
            'color': {
                'name': color,
                'elements': color_elements,
                'description': f"Using a {color} color palette with {', '.join(color_elements)}"
            },
            'material': {
                'name': material,
                'elements': material_elements,
                'description': f"Featuring {material} materials including {', '.join(material_elements)}"
            },
            'silhouette': {
                'name': silhouette,
                'elements': silhouette_elements,
                'description': f"With a {silhouette} silhouette emphasizing {', '.join(silhouette_elements)}"
            }
        }
        
        return creative_direction

    def parse_outfit_response(self, response_text: str) -> Dict:
        """Parse the outfit response from the language model."""
        logger.info("Starting to parse outfit response")
        logger.info(f"Raw response text:\n{response_text}")
        
        # Initialize outfit data with lists instead of sets
        outfit_data = {
            'top': None,
            'bottom': None,
            'shoes': None,
            'extras': None,
            'colors': [],
            'materials': [],
            'lengths': [],
            'textures': [],
            'styles': []
        }
        
        # Split response into lines and process
        lines = response_text.strip().split('\n')
        logger.info(f"Processing {len(lines)} lines from response")
        
        # First pass: Look for exact matches with ** format
        current_component = None
        component_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for component headers with ** format
            if '**Top:' in line:
                current_component = 'top'
                component_text = [line.split('**Top:')[1].strip()]
            elif '**Bottom:' in line:
                current_component = 'bottom'
                component_text = [line.split('**Bottom:')[1].strip()]
            elif '**Shoes:' in line:
                current_component = 'shoes'
                component_text = [line.split('**Shoes:')[1].strip()]
            elif '**Extras:' in line:
                current_component = 'extras'
                component_text = [line.split('**Extras:')[1].strip()]
            elif current_component and not line.startswith('**'):
                component_text.append(line)
            
            # Store component when we hit a new section or end of text
            if current_component and (line.startswith('**') or line == lines[-1]):
                outfit_data[current_component] = ' '.join(component_text).strip()
                logger.info(f"Found {current_component}: {outfit_data[current_component]}")
                current_component = None
                component_text = []
        
        # Second pass: Look for components without ** format if still missing
        if not all(outfit_data[comp] for comp in ['top', 'bottom', 'shoes']):
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Try to find components by keywords
                if not outfit_data['top'] and any(word in line.lower() for word in ['top:', 'shirt:', 'blouse:', 'jacket:']):
                    outfit_data['top'] = line.split(':', 1)[1].strip()
                    logger.info(f"Found top (keyword): {outfit_data['top']}")
                elif not outfit_data['bottom'] and any(word in line.lower() for word in ['bottom:', 'pants:', 'skirt:', 'trousers:']):
                    outfit_data['bottom'] = line.split(':', 1)[1].strip()
                    logger.info(f"Found bottom (keyword): {outfit_data['bottom']}")
                elif not outfit_data['shoes'] and any(word in line.lower() for word in ['shoes:', 'boots:', 'heels:', 'footwear:']):
                    outfit_data['shoes'] = line.split(':', 1)[1].strip()
                    logger.info(f"Found shoes (keyword): {outfit_data['shoes']}")
        
        # Clean up component descriptions
        for component in ['top', 'bottom', 'shoes', 'extras']:
            if outfit_data[component]:
                # Remove markdown formatting
                outfit_data[component] = outfit_data[component].replace('**', '').strip()
        
        # Extract features from each component
        for component in ['top', 'bottom', 'shoes', 'extras']:
            if outfit_data[component]:
                text = outfit_data[component].lower()
                
                # Extract colors
                for color in self.color_keywords:
                    if color in text and color not in outfit_data['colors']:
                        outfit_data['colors'].append(color)
                        logger.info(f"Found color: {color}")
                
                # Extract materials
                for material in self.material_keywords:
                    if material in text and material not in outfit_data['materials']:
                        outfit_data['materials'].append(material)
                        logger.info(f"Found material: {material}")
                
                # Extract lengths
                for length in self.length_keywords:
                    if length in text and length not in outfit_data['lengths']:
                        outfit_data['lengths'].append(length)
                        logger.info(f"Found length: {length}")
                
                # Extract textures
                for texture in self.texture_keywords:
                    if texture in text and texture not in outfit_data['textures']:
                        outfit_data['textures'].append(texture)
                        logger.info(f"Found texture: {texture}")
        
        # Calculate scores
        formality = self.calculate_formality_score(response_text)
        trendiness = self.calculate_trendiness_score(response_text)
        comfort = self.calculate_comfort_score(response_text)
        
        logger.info(f"Scores calculated - Formality: {formality}, Trendiness: {trendiness}, Comfort: {comfort}")
        
        # Add scores to outfit data
        outfit_data['formality'] = formality
        outfit_data['trendiness'] = trendiness
        outfit_data['comfort'] = comfort
        
        return outfit_data

    def initialize_catalog(self):
        """Initialize the outfit catalog CSV file if it doesn't exist."""
        if not os.path.exists('outfit_catalog.csv'):
            with open('outfit_catalog.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'outfit_id', 'timestamp', 'event', 'outfit_number', 'variation',
                    'style_categories', 'formality_score', 'trendiness_score', 'comfort_score',
                    'top', 'bottom', 'bra', 'panties', 'shoes', 'extras',
                    'colors', 'materials', 'lengths', 'textures',
                    'temperature_rating', 'season_appropriateness',
                    'generation_status', 'validation_status', 'error_message'
                ])
        
        # Initialize images catalog if it doesn't exist
        if not os.path.exists('outfit_images.csv'):
            with open('outfit_images.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'image_id', 'outfit_id', 'filename', 'generation_timestamp',
                    'prompt', 'revised_prompt', 'evaluation_status'
                ])
        
        # Create outfits directory if it doesn't exist
        os.makedirs('outfits', exist_ok=True)

    def calculate_temperature_rating(self, outfit_data: Dict) -> int:
        cool_materials = {'wool', 'leather', 'velvet', 'fleece'}
        warm_materials = {'cotton', 'linen', 'silk', 'chiffon'}
        materials = set(outfit_data.get('materials', []))
        rating = 5
        if materials & cool_materials:
            rating -= 2
        if materials & warm_materials:
            rating += 2
        lengths = set(outfit_data.get('lengths', []))
        if {'mini', 'short', 'cropped'} & lengths:
            rating += 1
        if {'maxi', 'long', 'full-length'} & lengths:
            rating -= 1
        return max(0, min(10, rating))

    def calculate_trendiness_score(self, all_text: str) -> int:
        trend_keywords = {
            'modern': 2, 'vintage': 1, 'minimalist': 2, 'bold': 1,
            'statement': 1, 'chic': 2, 'avant-garde': 2
        }
        score = 5
        for word, pts in trend_keywords.items():
            if word in all_text:
                score += pts
        return max(0, min(10, score))

    def calculate_comfort_score(self, all_text: str) -> int:
        comfort_keywords = {
            'casual': 2, 'comfortable': 2, 'relaxed': 1, 'soft': 1,
            'laid-back': 1, 'everyday': 1
        }
        score = 5
        for word, pts in comfort_keywords.items():
            if word in all_text:
                score += pts
        return max(0, min(10, score))

    def calculate_formality_score(self, all_text: str) -> int:
        """Calculate the formality score for an outfit description."""
        formality_indicators = {
            'formal': 2, 'elegant': 2, 'sophisticated': 2,
            'casual': -2, 'relaxed': -2, 'comfortable': -1,
            'structured': 1, 'tailored': 1, 'professional': 1
        }
        score = 5  # Default middle value
        for word, pts in formality_indicators.items():
            if word in all_text.lower():
                score += pts
        return max(0, min(10, score))

    def _generate_with_language_model(self, prompt: str) -> str:
        """Generate outfit description using the language model."""
        try:
            # Check if Ollama server is running
            try:
                logger.info("Checking Ollama server connection...")
                response = requests.get("http://localhost:11434/api/tags")
                response.raise_for_status()
                logger.info("Ollama server is running and accessible")
            except requests.exceptions.ConnectionError:
                logger.error("Ollama server is not running. Please start the Ollama server first.")
                return ""
            except requests.exceptions.RequestException as e:
                logger.error(f"Error connecting to Ollama server: {str(e)}")
                return ""

            # Generate outfit description
            logger.info("Sending prompt to language model...")
            logger.debug(f"Prompt: {prompt}")
            response = requests.post(
                self.ollama_url,
                json={
                    "model": "long-gemma",
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            logger.info("Received response from language model")
            logger.debug(f"Raw response: {result}")
            
            if "response" not in result:
                logger.error("No 'response' field in model output")
                return ""
                
            generated_text = result["response"]
            logger.info(f"Generated text length: {len(generated_text)} characters")
            logger.debug(f"Generated text: {generated_text}")
            return generated_text
        except Exception as e:
            logger.error(f"Error generating outfit: {str(e)}")
            return ""

    def generate_outfit_image(self, outfit_data: Dict, num_images: int = 1) -> List[str]:
        """Generate image(s) for an outfit using xAI API."""
        try:
            import os
            from openai import OpenAI
            
            XAI_API_KEY = os.getenv("XAI_API_KEY")
            if not XAI_API_KEY:
                raise ValueError("XAI_API_KEY not found in environment variables")
                
            client = OpenAI(base_url="https://api.x.ai/v1", api_key=XAI_API_KEY)
            
            # Create outfit directory if it doesn't exist
            outfit_dir = os.path.join('outfits', outfit_data['outfit_id'])
            os.makedirs(outfit_dir, exist_ok=True)
            
            # Construct detailed prompt by item, keeping it under 1024 characters
            prompt_parts = []
            
            # Top
            if outfit_data.get('top'):
                top_desc = outfit_data['top'].split('.')[0]  # Take first sentence for brevity
                prompt_parts.append(f"Top: {top_desc}")
            
            # Bottom
            if outfit_data.get('bottom'):
                bottom_desc = outfit_data['bottom'].split('.')[0]
                prompt_parts.append(f"Bottom: {bottom_desc}")
            
            # Shoes
            if outfit_data.get('shoes'):
                shoes_desc = outfit_data['shoes'].split('.')[0]
                prompt_parts.append(f"Shoes: {shoes_desc}")
            
            # Extras
            if outfit_data.get('extras'):
                extras_desc = outfit_data['extras'].split('.')[0]
                prompt_parts.append(f"Accessories: {extras_desc}")
            
            # Add style and color context
            if outfit_data.get('style_categories'):
                prompt_parts.append(f"Style: {outfit_data['style_categories']}")
            if outfit_data.get('colors'):
                prompt_parts.append(f"Color palette: {outfit_data['colors']}")
            
            # Combine parts with a focus on the overall aesthetic
            prompt = "Fashion illustration of: " + ". ".join(prompt_parts)
            prompt += ". High quality fashion illustration, detailed textures and materials."
            
            # Ensure prompt is under 1024 characters
            if len(prompt) > 1024:
                prompt = prompt[:1000] + ". High quality fashion illustration."
            
            logger.info(f"Generated prompt length: {len(prompt)}")
            
            response = client.images.generate(
                model="grok-2-image",
                prompt=prompt,
                n=num_images,
                response_format="b64_json"
            )
            
            image_filenames = []
            for idx, image_data in enumerate(response.data):
                # Save base64 image to file in outfit directory
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"image_{timestamp}_{idx}.jpg"
                filepath = os.path.join(outfit_dir, filename)
                
                with open(filepath, "wb") as f:
                    f.write(base64.b64decode(image_data.b64_json))
                
                # Save image metadata to images catalog
                self._save_image_metadata(
                    outfit_data['outfit_id'],
                    filename,
                    prompt,
                    image_data.revised_prompt
                )
                
                image_filenames.append(filepath)
            
            return image_filenames
            
        except Exception as e:
            logger.error(f"Error generating outfit image: {str(e)}")
            return []

    def _save_image_metadata(self, outfit_id: str, filename: str, prompt: str, revised_prompt: str):
        """Save image metadata to the images catalog."""
        try:
            with open('outfit_images.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                writer.writerow([
                    f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    outfit_id,
                    filename,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    prompt,
                    revised_prompt,
                    'Pending'
                ])
            logger.info(f"Saved image metadata for {filename}")
        except Exception as e:
            logger.error(f"Error saving image metadata: {str(e)}")

    def update_catalog_with_image(self, outfit_id: str, image_filename: str):
        """Update catalog entry with image information."""
        try:
            # Update images catalog
            df_images = pd.read_csv('outfit_images.csv')
            mask = df_images['outfit_id'] == outfit_id
            if mask.any():
                df_images.loc[mask, 'evaluation_status'] = 'Generated'
                df_images.to_csv('outfit_images.csv', index=False)
                logger.info(f"Updated images catalog for outfit {outfit_id}")
        except Exception as e:
            logger.error(f"Error updating catalog with image: {str(e)}")

    def cleanup_catalog(self):
        """Clean up the catalog by removing incomplete entries and duplicates."""
        try:
            if not os.path.exists('outfit_catalog.csv'):
                return
                
            # Read existing catalog
            df = pd.read_csv('outfit_catalog.csv')
            
            # Remove entries with missing required fields
            required_fields = ['style_categories', 'top', 'bottom', 'shoes', 'colors', 'materials']
            df = df.dropna(subset=required_fields)
            
            # Remove entries with default scores (5,5,5)
            df = df[~((df['formality_score'] == 5.0) & 
                     (df['trendiness_score'] == 5.0) & 
                     (df['comfort_score'] == 5.0))]
            
            # Remove duplicates based on event, outfit_number, and variation
            df = df.drop_duplicates(subset=['event', 'outfit_number', 'variation'])
            
            # Reset generation status for remaining entries
            df['generation_status'] = 'Success'
            df['validation_status'] = 'Valid'
            df['error_message'] = ''
            
            # Save cleaned catalog
            df.to_csv('outfit_catalog.csv', index=False)
            logger.info(f"Catalog cleaned: {len(df)} valid entries remaining")
            
            # Clean up images catalog
            if os.path.exists('outfit_images.csv'):
                df_images = pd.read_csv('outfit_images.csv')
                # Remove entries for outfits that no longer exist
                valid_outfits = set(df['outfit_id'])
                df_images = df_images[df_images['outfit_id'].isin(valid_outfits)]
                df_images.to_csv('outfit_images.csv', index=False)
                logger.info(f"Images catalog cleaned: {len(df_images)} valid entries remaining")
                
        except Exception as e:
            logger.error(f"Error during catalog cleanup: {str(e)}")
            logger.error(f"Error generating image: {str(e)}")
            return None

    def save_generation(self, prompt: str, image_data: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_prompt = "".join(x for x in prompt[:30] if x.isalnum() or x in (' ', '-', '_'))
        filename = f"{timestamp}_{safe_prompt}.png"
        image_path = self.output_dir / filename
        with open(image_path, 'wb') as f:
            f.write(base64.b64decode(image_data))
        entry = {"timestamp": timestamp, "prompt": prompt, "filename": filename}
        self.history.append(entry)
        self._save_history()
        logger.info(f"Saved image to: {image_path}")
        return filename

    def list_generations(self):
        if not self.history:
            print("No previous generations found.")
            return
        print("\nGeneration History:")
        print("-" * 80)
        for i, entry in enumerate(self.history, 1):
            print(f"{i}. [{entry['timestamp']}] {entry['prompt'][:50]}...")
            print(f"   File: {entry['filename']}\n")

    def view_generation(self, index: int):
        if 0 <= index < len(self.history):
            entry = self.history[index]
            print("\nGeneration Details:")
            print("-" * 80)
            print(f"Timestamp: {entry['timestamp']}")
            print(f"Prompt: {entry['prompt']}")
            print(f"File: {entry['filename']}")
            image_path = self.output_dir / entry['filename']
            if image_path.exists():
                print(f"Image exists at: {image_path}")
            else:
                print("Warning: Image file not found!")
        else:
            print("Invalid generation index!")


class ImageGenerator:
    """Base class for image generation functionality."""
    
    def __init__(self):
        """Initialize the image generator."""
        self.api_key = os.getenv('XAI_API_KEY')
        if not self.api_key:
            raise ValueError("XAI_API_KEY environment variable not set")
        
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        self.base_url = 'https://api.xai.com/v1/images/generations'
        
    def generate_image(self, prompt: str, size: str = "1024x1024", n: int = 1) -> List[str]:
        """Generate images based on the given prompt.
        
        Args:
            prompt (str): The prompt describing the image to generate
            size (str): The size of the image to generate
            n (int): Number of images to generate
            
        Returns:
            List[str]: List of image URLs
        """
        try:
            data = {
                "prompt": prompt,
                "size": size,
                "n": n,
                "response_format": "url"
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            return [img['url'] for img in result['data']]
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error generating image: {str(e)}")
            return []
            
    def download_image(self, url: str, save_path: str) -> bool:
        """Download an image from a URL and save it to the specified path.
        
        Args:
            url (str): URL of the image to download
            save_path (str): Path to save the image
            
        Returns:
            bool: True if download was successful, False otherwise
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading image: {str(e)}")
            return False

class EnhancedImageGenerator(ImageGenerator):
    """Enhanced image generator that integrates with the outfit generator."""
    def __init__(self):
        super().__init__()
        self.outfit_generator = OutfitGenerator()
        logger.info("Enhanced image generator initialized")

    def generate_outfit_image(self, outfit_data: Dict) -> Optional[str]:
        components = [
            ('Top', outfit_data.get('top', '')),
            ('Bottom', outfit_data.get('bottom', '')),
            ('Shoes', outfit_data.get('shoes', '')),
            ('Extras', outfit_data.get('extras', ''))
        ]
        valid_components = [(name, desc) for name, desc in components if desc.strip()]
        logger.debug(f"Valid components: {valid_components}")
        if not valid_components:
            logger.warning("No valid outfit descriptions found, skipping image generation")
            return None
        styles = outfit_data.get('styles', [])
        style_context = f"in a {', '.join(styles).lower()} style" if styles else ""
        prompt = f"Professional fashion photography of a woman wearing an outfit {style_context}: "
        for name, desc in valid_components:
            prompt += f"{name}: {desc}. "
        logger.info(f"Generating image with prompt: {prompt}")
        image_filename = self.generate_image(prompt)
        logger.debug(f"Generated image filename: {image_filename}")
        if image_filename:
            self.update_catalog_with_image(outfit_data['timestamp'], image_filename)
            logger.info(f"Updated catalog with image filename: {image_filename}")
        return image_filename

    def update_catalog_with_image(self, timestamp: str, image_filename: str):
        # Read the CSV using engine='python' and specifying the quotechar.
        df = pd.read_csv(self.outfit_generator.catalog_file, engine='python', quotechar='"')
        df.loc[df['timestamp'] == timestamp, 'image_filename'] = image_filename
        df.to_csv(self.outfit_generator.catalog_file, index=False, quoting=csv.QUOTE_ALL)
        logger.info(f"Catalog updated for timestamp {timestamp} with image filename {image_filename}")


#############################
#    VISION EVALUATOR       #
#############################

class VisionEvaluator:
    """
    Uses xAI's vision model to evaluate a generated outfit image. The model
    accepts messages that include both image (Base64 or URL) and text.
    """
    def __init__(self):
        self.api_key = os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise Exception("XAI_API_KEY not set in environment")
        self.base_url = "https://api.x.ai/v1/chat/completions"
        self.model = "grok-2-vision-latest"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def encode_image(self, image_path: Path) -> str:
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")
        return encoded

    def evaluate_outfit_image(self, image_filename: str, text_prompt: str) -> str:
        image_path = Path("generated_images") / image_filename
        if not image_path.exists():
            return "Image file not found."
        base64_image = self.encode_image(image_path)
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    },
                    {
                        "type": "text",
                        "text": text_prompt
                    }
                ]
            }
        ]
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.01
        }
        try:
            logger.info("Sending evaluation request to vision model.")
            response = requests.post(self.base_url, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()
            evaluation = result["choices"][0]["message"]["content"]
            logger.info("Received evaluation from vision model.")
            return evaluation
        except Exception as e:
            logger.error(f"Error evaluating image: {str(e)}")
            return "Error during image evaluation."


#############################
#         TO-DO LIST        #
#############################

def show_todo_list():
    todo_items = [
        "Refactor asynchronous calls to fully integrate with outfit generation.",
        "Improve error handling and logging throughout the system.",
        "Add more detailed analytics in catalog statistics.",
        "Implement unit tests for each module.",
        "Optimize image generation performance and rate limiting.",
        "Enhance UI/UX for TUI, including better input validation.",
        "Research integration with additional vision models.",
        "Improve prompt design based on user feedback.",
        "Document the code for easier future maintenance.",
    ]
    print("\nTo-Do List:")
    print("-" * 40)
    for i, item in enumerate(todo_items, 1):
        print(f"{i}. {item}")
    print("-" * 40)


#############################
#           TUI             #
#############################

def main_tui():
    """Main Text User Interface for the outfit generator."""
    generator = OutfitGenerator()
    vision_evaluator = VisionEvaluator()
    openai_generator = OpenAIImageGenerator()
    
    while True:
        print("\n=== Outfit Generator Menu ===")
        print("1. Generate new outfits")
        print("2. Generate images for existing outfits")
        print("3. View outfit catalog")
        print("4. Review generated images")
        print("5. Evaluate outfit images")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == "1":
            event = input("Enter event type: ")
            try:
                num_outfits = int(input("Number of outfits to generate: "))
                variations = int(input("Variations per outfit: "))
            except ValueError:
                print("Please enter valid numbers!")
                continue
                
            outfits = generator.generate_outfit(event, num_outfits, variations)
            print(f"\nGenerated {len(outfits)} outfits successfully!")
            
            # Ask about image generation
            if input("\nGenerate images for these outfits? (y/n): ").lower() == 'y':
                # Choose image generation model
                print("\nChoose image generation model:")
                print("1. xAI (Default)")
                print("2. OpenAI GPT Image")
                model_choice = input("Enter choice (1-2): ")
                
                # Get quality setting for OpenAI
                quality = 'medium'
                if model_choice == "2":
                    print("\nChoose image quality:")
                    print("1. Low (faster, less detailed)")
                    print("2. Medium (balanced)")
                    print("3. High (slower, more detailed)")
                    quality_choice = input("Enter choice (1-3): ")
                    quality = {'1': 'low', '2': 'medium', '3': 'high'}.get(quality_choice, 'medium')
                
                # Ask for avatar image
                avatar_image = None
                if input("\nDo you have an avatar image to use as reference? (y/n): ").lower() == 'y':
                    avatar_path = input("Enter path to avatar image: ")
                    if os.path.exists(avatar_path):
                        avatar_image = avatar_path
                    else:
                        print("Avatar image not found!")
                
                for outfit in outfits:
                    if outfit.get('generation_status') == 'Success':
                        try:
                            num_images = int(input(f"How many images for outfit {outfit['outfit_number']} variation {outfit['variation']}? (1-10): "))
                            if 1 <= num_images <= 10:
                                if model_choice == "2":
                                    image_filenames = openai_generator.generate_outfit_image(
                                        outfit, 
                                        quality=quality,
                                        num_images=num_images,
                                        avatar_image=avatar_image
                                    )
                                else:
                                    image_filenames = generator.generate_outfit_image(outfit, num_images)
                                print(f"Generated {len(image_filenames)} images for this outfit")
                        except ValueError:
                            print("Please enter a valid number between 1 and 10!")
            
        elif choice == "2":
            try:
                # Load and validate catalog
                if not os.path.exists('outfit_catalog.csv'):
                    print("\nNo catalog found! Please generate some outfits first.")
                    continue
                    
                df = pd.read_csv('outfit_catalog.csv')
                
                # Ensure required columns exist
                required_columns = ['image_generated', 'generation_status']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    print("\nCatalog needs to be updated. Please wait...")
                    generator.migrate_catalog()
                    df = pd.read_csv('outfit_catalog.csv')
                
                # Filter for outfits without images
                no_images = df[(df['image_generated'] != 'True') & (df['generation_status'] == 'Success')]
                
                if no_images.empty:
                    print("\nNo outfits found without images!")
                    continue
                    
                print("\nOutfits without images:")
                for idx, row in no_images.iterrows():
                    print(f"{idx + 1}. Outfit {row['outfit_number']} variation {row['variation']} for {row['event']}")
                
                selection = input("\nEnter outfit number to generate image for (or 'all' for all outfits): ")
                
                if selection.lower() == 'all':
                    # Choose image generation model
                    print("\nChoose image generation model:")
                    print("1. xAI (Default)")
                    print("2. OpenAI GPT Image")
                    model_choice = input("Enter choice (1-2): ")
                    
                    # Get quality setting for OpenAI
                    quality = 'medium'
                    if model_choice == "2":
                        print("\nChoose image quality:")
                        print("1. Low (faster, less detailed)")
                        print("2. Medium (balanced)")
                        print("3. High (slower, more detailed)")
                        quality_choice = input("Enter choice (1-3): ")
                        quality = {'1': 'low', '2': 'medium', '3': 'high'}.get(quality_choice, 'medium')
                    
                    # Ask for avatar image
                    avatar_image = None
                    if input("\nDo you have an avatar image to use as reference? (y/n): ").lower() == 'y':
                        avatar_path = input("Enter path to avatar image: ")
                        if os.path.exists(avatar_path):
                            avatar_image = avatar_path
                        else:
                            print("Avatar image not found!")
                    
                    try:
                        num_images = int(input("How many images per outfit? (1-10): "))
                        if 1 <= num_images <= 10:
                            for _, row in no_images.iterrows():
                                outfit_data = row.to_dict()
                                if model_choice == "2":
                                    image_filenames = openai_generator.generate_outfit_image(
                                        outfit_data,
                                        quality=quality,
                                        num_images=num_images,
                                        avatar_image=avatar_image
                                    )
                                else:
                                    image_filenames = generator.generate_outfit_image(outfit_data, num_images)
                                print(f"Generated {len(image_filenames)} images for outfit {outfit_data['outfit_number']} variation {outfit_data['variation']}")
                    except ValueError:
                        print("Please enter a valid number between 1 and 10!")
                else:
                    try:
                        idx = int(selection) - 1
                        if 0 <= idx < len(no_images):
                            outfit_data = no_images.iloc[idx].to_dict()
                            
                            # Choose image generation model
                            print("\nChoose image generation model:")
                            print("1. xAI (Default)")
                            print("2. OpenAI GPT Image")
                            model_choice = input("Enter choice (1-2): ")
                            
                            # Get quality setting for OpenAI
                            quality = 'medium'
                            if model_choice == "2":
                                print("\nChoose image quality:")
                                print("1. Low (faster, less detailed)")
                                print("2. Medium (balanced)")
                                print("3. High (slower, more detailed)")
                                quality_choice = input("Enter choice (1-3): ")
                                quality = {'1': 'low', '2': 'medium', '3': 'high'}.get(quality_choice, 'medium')
                            
                            # Ask for avatar image
                            avatar_image = None
                            if input("\nDo you have an avatar image to use as reference? (y/n): ").lower() == 'y':
                                avatar_path = input("Enter path to avatar image: ")
                                if os.path.exists(avatar_path):
                                    avatar_image = avatar_path
                                else:
                                    print("Avatar image not found!")
                            
                            num_images = int(input("How many images? (1-10): "))
                            if 1 <= num_images <= 10:
                                if model_choice == "2":
                                    image_filenames = openai_generator.generate_outfit_image(
                                        outfit_data,
                                        quality=quality,
                                        num_images=num_images,
                                        avatar_image=avatar_image
                                    )
                                else:
                                    image_filenames = generator.generate_outfit_image(outfit_data, num_images)
                                print(f"Generated {len(image_filenames)} images")
                        else:
                            print("Invalid selection!")
                    except ValueError:
                        print("Please enter a valid number!")
                        
            except Exception as e:
                print(f"Error accessing catalog: {str(e)}")
                
        elif choice == "3":
            try:
                if not os.path.exists('outfit_catalog.csv'):
                    print("\nNo catalog found! Please generate some outfits first.")
                    continue
                    
                df = pd.read_csv('outfit_catalog.csv')
                print("\nOutfit Catalog:")
                print("-" * 80)
                for idx, row in df.iterrows():
                    print(f"{idx + 1}. Outfit {row['outfit_number']} variation {row['variation']} for {row['event']}")
                    print(f"   Style: {row['style_categories']}")
                    print(f"   Colors: {row['colors']}")
                    print(f"   Materials: {row['materials']}")
                    print(f"   Image Generated: {row['image_generated']}")
                    print("-" * 80)
                    
            except Exception as e:
                print(f"Error viewing catalog: {str(e)}")
                
        elif choice == "4":
            try:
                if not os.path.exists('outfit_catalog.csv'):
                    print("\nNo catalog found! Please generate some outfits first.")
                    continue
                    
                df = pd.read_csv('outfit_catalog.csv')
                images = df[df['image_generated'] == 'True']
                
                if images.empty:
                    print("\nNo images found in catalog!")
                    continue
                    
                print("\nGenerated Images:")
                for idx, row in images.iterrows():
                    print(f"{idx + 1}. {row['image_filename']} - Outfit {row['outfit_number']} variation {row['variation']} for {row['event']}")
                
                try:
                    index = int(input("\nEnter the number of the image to view (or 0 to go back): ")) - 1
                    if index == -1:
                        continue
                    if 0 <= index < len(images):
                        img_file = images.iloc[index]['image_filename']
                        if os.path.exists(img_file):
                            print(f"\nViewing image: {img_file}")
                            # Here you would add code to display the image
                            # For now, just show the path
                            print(f"Image path: {os.path.abspath(img_file)}")
                        else:
                            print(f"Image file not found: {img_file}")
                    else:
                        print("Invalid selection!")
                except ValueError:
                    print("Please enter a valid number!")
                    
            except Exception as e:
                print(f"Error reviewing images: {str(e)}")
                
        elif choice == "5":
            try:
                if not os.path.exists('outfit_catalog.csv'):
                    print("\nNo catalog found! Please generate some outfits first.")
                    continue
                    
                df = pd.read_csv('outfit_catalog.csv')
                images = df[df['image_generated'] == 'True']
                
                if images.empty:
                    print("\nNo images found in catalog!")
                    continue
                    
                print("\nAvailable Images for Evaluation:")
                for idx, row in images.iterrows():
                    print(f"{idx + 1}. {row['image_filename']} - Outfit {row['outfit_number']} variation {row['variation']}")
                
                try:
                    index = int(input("\nEnter the number of the image to evaluate (or 0 to go back): ")) - 1
                    if index == -1:
                        continue
                    if 0 <= index < len(images):
                        img_file = images.iloc[index]['image_filename']
                        if os.path.exists(img_file):
                            eval_prompt = ("Please evaluate this outfit image with respect to the prompt details. "
                                         "Provide numerical scores (0-10) for adherence, creativity, style, and overall aesthetic, "
                                         "along with a short critical review.")
                            evaluation = vision_evaluator.evaluate_outfit_image(img_file, eval_prompt)
                            print("\nEvaluation from Vision Model:")
                            print("-" * 40)
                            print(evaluation)
                        else:
                            print(f"Image file not found: {img_file}")
                    else:
                        print("Invalid selection!")
                except ValueError:
                    print("Please enter a valid number!")
                    
            except Exception as e:
                print(f"Error evaluating images: {str(e)}")
                
        elif choice == "6":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice! Please try again.")

        time.sleep(1)


class OutfitStoryGenerator:
    """Generates narrative and emotional context for outfits."""
    def __init__(self):
        self.story_templates = {
            'real_world': {
                'wedding': {
                    'template': "As {name} steps into the {venue}, the {time_of_day} light catches the {material} of their {garment}, creating a moment of pure {emotion}. The {color} hues reflect their {personality_trait}, while the {texture} details whisper of {backstory}.",
                    'emotions': ['joy', 'anticipation', 'nervousness', 'excitement'],
                    'personality_traits': ['elegance', 'confidence', 'grace', 'charm'],
                    'backstories': ['childhood dreams', 'family traditions', 'personal journey', 'romantic story']
                },
                'interview': {
                    'template': "Walking into the {company} headquarters, {name} carries themselves with {confidence_level}. The {material} {garment} speaks of {professional_trait}, while the {color} tones project {career_quality}. Every {detail} tells a story of {achievement}.",
                    'emotions': ['determination', 'focus', 'ambition', 'preparedness'],
                    'professional_traits': ['expertise', 'experience', 'knowledge', 'skill'],
                    'career_qualities': ['reliability', 'innovation', 'leadership', 'excellence']
                },
                'date': {
                    'template': "As {name} enters the {venue}, their {garment} catches the {lighting}, creating an aura of {mood}. The {color} tones reflect their {emotional_state}, while the {texture} details hint at their {intention}.",
                    'emotions': ['excitement', 'nervousness', 'anticipation', 'curiosity'],
                    'moods': ['romance', 'mystery', 'playfulness', 'sophistication'],
                    'intentions': ['connection', 'adventure', 'discovery', 'passion']
                }
            },
            'character': {
                'fantasy': {
                    'template': "In the {location}, {name} stands as a {role}, their {garment} shimmering with {magical_quality}. The {color} hues pulse with {power_type}, while the {texture} details reveal their {character_trait}. Every {detail} tells of their {backstory}.",
                    'magical_qualities': ['ancient power', 'elemental energy', 'mystical aura', 'enchanted essence'],
                    'power_types': ['arcane', 'divine', 'elemental', 'shadow'],
                    'character_traits': ['wisdom', 'courage', 'mystery', 'nobility']
                },
                'historical': {
                    'template': "Amidst the {era} {setting}, {name} moves with {social_status}, their {garment} reflecting the {cultural_context}. The {color} tones speak of their {background}, while the {texture} details reveal their {personal_quality}. Every {detail} tells of their {life_story}.",
                    'social_statuses': ['noble grace', 'common dignity', 'royal bearing', 'artisan pride'],
                    'cultural_contexts': ['traditions', 'customs', 'values', 'heritage'],
                    'personal_qualities': ['resilience', 'wisdom', 'strength', 'grace']
                }
            }
        }
        
        self.emotional_contexts = {
            'joy': {'intensity': 8, 'warmth': 7, 'energy': 6},
            'anticipation': {'intensity': 7, 'warmth': 5, 'energy': 8},
            'nervousness': {'intensity': 6, 'warmth': 3, 'energy': 7},
            'excitement': {'intensity': 9, 'warmth': 6, 'energy': 9},
            'determination': {'intensity': 8, 'warmth': 4, 'energy': 7},
            'focus': {'intensity': 7, 'warmth': 3, 'energy': 6},
            'ambition': {'intensity': 8, 'warmth': 5, 'energy': 8},
            'preparedness': {'intensity': 7, 'warmth': 4, 'energy': 6}
        }
        
    def generate_story(self, outfit_data: Dict, context: Dict) -> Dict:
        """Generate a narrative story for the outfit."""
        is_character = outfit_data.get('is_character_outfit', False)
        event = outfit_data.get('event', '').lower()
        story_type = 'character' if is_character else 'real_world'
        
        if event not in self.story_templates[story_type]:
            return {
                'story': "No specific story template available for this event.",
                'emotional_context': {'intensity': 5, 'warmth': 5, 'energy': 5}
            }
            
        template = self.story_templates[story_type][event]
        story_context = self._prepare_story_context(outfit_data, context, template)
        story = self._fill_template(template['template'], story_context)
        
        emotional_context = self._generate_emotional_context(story_context)
        
        return {
            'story': story,
            'emotional_context': emotional_context,
            'story_elements': story_context
        }
        
    def _prepare_story_context(self, outfit_data: Dict, context: Dict, template: Dict) -> Dict:
        """Prepare the context for story generation."""
        components = outfit_data.get('components', {})
        features = outfit_data.get('features', {})
        
        story_context = {
            'name': context.get('name', 'the wearer'),
            'venue': context.get('venue', 'venue'),
            'time_of_day': context.get('time_of_day', 'evening'),
            'material': features.get('materials', ['fabric'])[0],
            'garment': components.get('top', 'outfit'),
            'color': features.get('colors', ['color'])[0],
            'texture': features.get('textures', ['texture'])[0],
            'detail': components.get('extras', 'details')
        }
        
        # Add template-specific elements
        for key in template.keys():
            if key != 'template' and isinstance(template[key], list):
                story_context[key] = random.choice(template[key])
                
        return story_context
        
    def _fill_template(self, template: str, context: Dict) -> str:
        """Fill the story template with context values."""
        story = template
        for key, value in context.items():
            story = story.replace(f"{{{key}}}", str(value))
        return story
        
    def _generate_emotional_context(self, story_context: Dict) -> Dict:
        """Generate emotional context for the story."""
        emotion = story_context.get('emotion', 'neutral')
        if emotion in self.emotional_contexts:
            return self.emotional_contexts[emotion]
        return {'intensity': 5, 'warmth': 5, 'energy': 5}


class CulturalValidator:
    """Validates outfits against cultural and historical standards."""
    def __init__(self):
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
                },
                'casual': {
                    'required': ['top', 'bottom', 'footwear'],
                    'forbidden': ['formal_wear', 'business_attire'],
                    'materials': ['cotton', 'denim', 'knit'],
                    'colors': ['any']
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
            },
            'middle_eastern': {
                'traditional': {
                    'required': ['thobe', 'ghutra', 'agal'],
                    'forbidden': ['western_formal'],
                    'materials': ['cotton', 'wool'],
                    'colors': ['white', 'black', 'brown']
                },
                'formal': {
                    'required': ['bisht', 'formal_thobe'],
                    'forbidden': ['casual_wear'],
                    'materials': ['wool', 'silk'],
                    'colors': ['black', 'navy', 'gray']
                }
            }
        }
        
        self.historical_periods = {
            'victorian': {
                'women': {
                    'required': ['corset', 'petticoat', 'bustle'],
                    'forbidden': ['pants', 'short_skirts'],
                    'materials': ['silk', 'lace', 'velvet'],
                    'colors': ['black', 'navy', 'burgundy', 'forest_green']
                },
                'men': {
                    'required': ['tailcoat', 'waistcoat', 'cravat'],
                    'forbidden': ['casual_wear'],
                    'materials': ['wool', 'silk'],
                    'colors': ['black', 'navy', 'gray']
                }
            },
            'medieval': {
                'women': {
                    'required': ['tunic', 'girdle', 'veil'],
                    'forbidden': ['modern_clothing'],
                    'materials': ['wool', 'linen'],
                    'colors': ['earth_tones', 'natural_dyes']
                },
                'men': {
                    'required': ['tunic', 'hose', 'belt'],
                    'forbidden': ['modern_clothing'],
                    'materials': ['wool', 'linen'],
                    'colors': ['earth_tones', 'natural_dyes']
                }
            }
        }
    
    def validate_outfit(self, outfit_data: Dict, culture: str = 'western', 
                       period: Optional[str] = None) -> Dict:
        """
        Validates an outfit against cultural and historical standards.
        
        Args:
            outfit_data (Dict): The outfit data to validate
            culture (str): The cultural context to validate against
            period (Optional[str]): The historical period to validate against
            
        Returns:
            Dict containing validation results and suggestions
        """
        components = outfit_data.get('components', {})
        features = outfit_data.get('features', {})
        
        validation_results = {
            'is_valid': True,
            'violations': [],
            'suggestions': [],
            'cultural_score': 100,
            'historical_score': 100 if period else None
        }
        
        # Validate against cultural standards
        if culture in self.cultural_rules:
            cultural_rules = self.cultural_rules[culture]
            style = outfit_data.get('style', 'casual')
            
            if style in cultural_rules:
                rules = cultural_rules[style]
                
                # Check required items
                for item in rules['required']:
                    if item not in components:
                        validation_results['violations'].append(f"Missing required {item}")
                        validation_results['cultural_score'] -= 10
                
                # Check forbidden items
                for item in rules['forbidden']:
                    if item in components:
                        validation_results['violations'].append(f"Forbidden {item} present")
                        validation_results['cultural_score'] -= 15
                
                # Check materials
                outfit_materials = set(features.get('materials', []))
                if 'materials' in rules and rules['materials'] != ['any']:
                    valid_materials = set(rules['materials'])
                    invalid_materials = outfit_materials - valid_materials
                    if invalid_materials:
                        validation_results['violations'].append(
                            f"Invalid materials: {', '.join(invalid_materials)}"
                        )
                        validation_results['cultural_score'] -= 5 * len(invalid_materials)
                
                # Check colors
                outfit_colors = set(features.get('colors', []))
                if 'colors' in rules and rules['colors'] != ['any']:
                    valid_colors = set(rules['colors'])
                    invalid_colors = outfit_colors - valid_colors
                    if invalid_colors:
                        validation_results['violations'].append(
                            f"Invalid colors: {', '.join(invalid_colors)}"
                        )
                        validation_results['cultural_score'] -= 5 * len(invalid_colors)
        
        # Validate against historical standards if period is specified
        if period and period in self.historical_periods:
            period_rules = self.historical_periods[period]
            gender = outfit_data.get('gender', 'women')
            
            if gender in period_rules:
                rules = period_rules[gender]
                
                # Check required items
                for item in rules['required']:
                    if item not in components:
                        validation_results['violations'].append(
                            f"Missing historically required {item}"
                        )
                        validation_results['historical_score'] -= 10
                
                # Check forbidden items
                for item in rules['forbidden']:
                    if item in components:
                        validation_results['violations'].append(
                            f"Historically forbidden {item} present"
                        )
                        validation_results['historical_score'] -= 15
                
                # Check materials
                outfit_materials = set(features.get('materials', []))
                valid_materials = set(rules['materials'])
                invalid_materials = outfit_materials - valid_materials
                if invalid_materials:
                    validation_results['violations'].append(
                        f"Historically invalid materials: {', '.join(invalid_materials)}"
                    )
                    validation_results['historical_score'] -= 5 * len(invalid_materials)
                
                # Check colors
                outfit_colors = set(features.get('colors', []))
                valid_colors = set(rules['colors'])
                invalid_colors = outfit_colors - valid_colors
                if invalid_colors:
                    validation_results['violations'].append(
                        f"Historically invalid colors: {', '.join(invalid_colors)}"
                    )
                    validation_results['historical_score'] -= 5 * len(invalid_colors)
        
        # Generate suggestions based on violations
        if validation_results['violations']:
            validation_results['is_valid'] = False
            validation_results['suggestions'] = self._generate_suggestions(
                validation_results['violations'],
                culture,
                period
            )
        
        return validation_results
    
    def _generate_suggestions(self, violations: List[str], 
                            culture: str, period: Optional[str]) -> List[str]:
        """Generate suggestions to fix validation violations."""
        suggestions = []
        
        for violation in violations:
            if "Missing required" in violation:
                item = violation.split("required ")[1]
                suggestions.append(f"Add a {item} to complete the outfit")
            elif "Forbidden" in violation:
                item = violation.split(" ")[1]
                suggestions.append(f"Remove the {item} as it's not appropriate")
            elif "Invalid materials" in violation:
                materials = violation.split(": ")[1]
                suggestions.append(
                    f"Replace {materials} with culturally appropriate materials"
                )
            elif "Invalid colors" in violation:
                colors = violation.split(": ")[1]
                suggestions.append(
                    f"Replace {colors} with culturally appropriate colors"
                )
        
        return suggestions


class OpenAIImageGenerator:
    """OpenAI GPT Image API implementation for outfit image generation."""
    
    def __init__(self):
        """Initialize the OpenAI image generator."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=self.api_key)
        self.quality_options = {
            'low': {'tokens': 272, 'quality': 'low'},
            'medium': {'tokens': 1056, 'quality': 'medium'},
            'high': {'tokens': 4160, 'quality': 'high'}
        }
        
    def generate_outfit_image(self, outfit_data: Dict, quality: str = 'medium', 
                            size: str = "1024x1024", num_images: int = 1,
                            avatar_image: Optional[str] = None) -> List[str]:
        """Generate outfit images using OpenAI's GPT Image API.
        
        Args:
            outfit_data (Dict): Outfit description data
            quality (str): Image quality ('low', 'medium', 'high')
            size (str): Image size (e.g., "1024x1024")
            num_images (int): Number of images to generate
            avatar_image (Optional[str]): Path to avatar image for reference
            
        Returns:
            List[str]: List of generated image filenames
        """
        try:
            # Validate and prepare outfit data
            if not isinstance(outfit_data, dict):
                raise ValueError("outfit_data must be a dictionary")
            
            # Generate outfit_id if not present
            if 'outfit_id' not in outfit_data:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                outfit_data['outfit_id'] = f"outfit_{timestamp}"
            
            # Create outfit directory if it doesn't exist
            outfit_dir = os.path.join('outfits', outfit_data['outfit_id'])
            os.makedirs(outfit_dir, exist_ok=True)
            
            # Construct detailed prompt
            prompt_parts = []
            
            # Add avatar reference if provided
            if avatar_image and os.path.exists(avatar_image):
                prompt_parts.append("Reference image of the wearer's face and style:")
            
            # Add outfit components
            if outfit_data.get('top'):
                prompt_parts.append(f"Top: {outfit_data['top']}")
            if outfit_data.get('bottom'):
                prompt_parts.append(f"Bottom: {outfit_data['bottom']}")
            if outfit_data.get('shoes'):
                prompt_parts.append(f"Shoes: {outfit_data['shoes']}")
            if outfit_data.get('extras'):
                prompt_parts.append(f"Accessories: {outfit_data['extras']}")
            
            # Add style and color context
            if outfit_data.get('style_categories'):
                prompt_parts.append(f"Style: {outfit_data['style_categories']}")
            if outfit_data.get('colors'):
                prompt_parts.append(f"Color palette: {outfit_data['colors']}")
            
            # Combine parts with a focus on the overall aesthetic
            prompt = "Professional fashion photography of: " + ". ".join(prompt_parts)
            prompt += ". High quality fashion photography, detailed textures and materials."
            
            # Ensure prompt is under 1024 characters
            if len(prompt) > 1024:
                prompt = prompt[:1000] + ". High quality fashion photography."
            
            # Prepare image generation parameters
            params = {
                "model": "gpt-image-1",
                "prompt": prompt,
                "n": num_images,
                "size": size
            }
            
            # Add quality parameter if specified
            if quality in self.quality_options:
                params["quality"] = self.quality_options[quality]['quality']
            
            # Generate images
            response = self.client.images.generate(**params)
            
            image_filenames = []
            for idx, image_data in enumerate(response.data):
                # Save base64 image to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"openai_image_{timestamp}_{idx}.png"
                filepath = os.path.join(outfit_dir, filename)
                
                with open(filepath, "wb") as f:
                    f.write(base64.b64decode(image_data.b64_json))
                
                # Save image metadata
                self._save_image_metadata(
                    outfit_data['outfit_id'],
                    filename,
                    prompt,
                    image_data.revised_prompt if hasattr(image_data, 'revised_prompt') else prompt
                )
                
                image_filenames.append(filepath)
            
            return image_filenames
            
        except Exception as e:
            logger.error(f"Error generating outfit image with OpenAI: {str(e)}")
            return []
    
    def _save_image_metadata(self, outfit_id: str, filename: str, prompt: str, revised_prompt: str):
        """Save image metadata to the images catalog."""
        try:
            with open('outfit_images.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                writer.writerow([
                    f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    outfit_id,
                    filename,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    prompt,
                    revised_prompt,
                    'Pending'
                ])
            logger.info(f"Saved OpenAI image metadata for {filename}")
        except Exception as e:
            logger.error(f"Error saving OpenAI image metadata: {str(e)}")


class PromptManager:
    def __init__(self):
        self.prompt_versions = {}
        self.current_versions = {}
        self._initialize_prompt_modules()
    
    def _initialize_prompt_modules(self):
        """Initialize all prompt modules with their versions."""
        # Base style module
        self.add_module('base_style', {
            'v1': "Create a {style} outfit that is {style_adj} and {style_adj2}.",
            'v2': "Design a {style} look that embodies {style_adj} and {style_adj2} elements.",
            'v3': "Craft a {style} ensemble that showcases {style_adj} and {style_adj2} characteristics."
        })
        
        # Garment description module
        self.add_module('garment_desc', {
            'v1': "The outfit should include a {top}, {bottom}, and {shoes}.",
            'v2': "The look should feature a {top} paired with {bottom} and {shoes}.",
            'v3': "The ensemble should consist of a {top}, complemented by {bottom} and {shoes}."
        })
        
        # Style context module
        self.add_module('style_context', {
            'v1': "The style should be appropriate for a {event} event.",
            'v2': "The look should be suitable for a {event} occasion.",
            'v3': "The outfit should be perfect for a {event} setting."
        })
        
        # Technical requirements module
        self.add_module('tech_req', {
            'v1': "Ensure the outfit is {material} and {material2}.",
            'v2': "The garments should be made of {material} and {material2}.",
            'v3': "Use {material} and {material2} materials for the outfit."
        })
        
        # Mood and atmosphere module
        self.add_module('mood', {
            'v1': "The overall mood should be {mood} and {mood2}.",
            'v2': "Create a {mood} and {mood2} atmosphere with the outfit.",
            'v3': "The look should convey a {mood} and {mood2} feeling."
        })
        
        # Model pose module
        self.add_module('model_pose', {
            'v1': "The model should be posed in a {pose} position.",
            'v2': "Show the outfit with the model in a {pose} stance.",
            'v3': "Present the look with the model in a {pose} pose."
        })
    
    def add_module(self, name: str, versions: Dict[str, str]):
        """Add a new prompt module with its versions."""
        self.prompt_versions[name] = versions
        self.current_versions[name] = list(versions.keys())[0]
    
    def add_version(self, module: str, version: str, template: str):
        """Add a new version to an existing prompt module."""
        if module in self.prompt_versions:
            self.prompt_versions[module][version] = template
        else:
            self.add_module(module, {version: template})
    
    def get_current_template(self, module: str) -> str:
        """Get the current template for a module."""
        if module in self.prompt_versions:
            return self.prompt_versions[module][self.current_versions[module]]
        return ""
    
    def compose_fashion_prompt(self, outfit_data: Dict) -> str:
        """Compose a complete fashion photography prompt based on outfit data."""
        # Get current templates for each module
        base_style = self.get_current_template('base_style')
        garment_desc = self.get_current_template('garment_desc')
        style_context = self.get_current_template('style_context')
        tech_req = self.get_current_template('tech_req')
        mood = self.get_current_template('mood')
        model_pose = self.get_current_template('model_pose')
        
        # Get style adjectives
        style = outfit_data.get('style', 'classic')
        style_adj = outfit_data.get('style_adj', 'elegant')
        style_adj2 = outfit_data.get('style_adj2', 'sophisticated')
        
        # Get garment details
        top = outfit_data.get('top', 'blouse')
        bottom = outfit_data.get('bottom', 'pants')
        shoes = outfit_data.get('shoes', 'heels')
        
        # Get event and materials
        event = outfit_data.get('event', 'formal')
        material = outfit_data.get('material', 'silk')
        material2 = outfit_data.get('material2', 'cotton')
        
        # Get mood and pose
        mood1 = outfit_data.get('mood', 'elegant')
        mood2 = outfit_data.get('mood2', 'sophisticated')
        pose = outfit_data.get('pose', 'standing')
        
        # Compose the prompt
        prompt_parts = [
            base_style.format(style=style, style_adj=style_adj, style_adj2=style_adj2),
            garment_desc.format(top=top, bottom=bottom, shoes=shoes),
            style_context.format(event=event),
            tech_req.format(material=material, material2=material2),
            mood.format(mood=mood1, mood2=mood2),
            model_pose.format(pose=pose)
        ]
        
        # Add any additional elements
        if 'extras' in outfit_data:
            extras = outfit_data['extras']
            if extras:
                prompt_parts.append(f"Accessories should include {', '.join(extras)}.")
        
        # Combine all parts
        return " ".join(prompt_parts)


if __name__ == "__main__":
    main_tui()