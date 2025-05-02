"""
Style context and definitions for outfit generation
"""
from enum import Enum, auto
from dataclasses import dataclass
from typing import Set, Dict, Optional

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
class StyleContext:
    """Context for style-based outfit generation"""
    primary_style: Style
    secondary_styles: Set[Style]
    formality_level: int  # 1-10 scale
    occasion_type: str
    season: Optional[str] = None
    time_of_day: Optional[str] = None
    weather_conditions: Optional[str] = None
    cultural_context: Optional[Dict[str, str]] = None
    
    def is_formal(self) -> bool:
        """Check if style context is formal"""
        return self.formality_level >= 7
    
    def is_casual(self) -> bool:
        """Check if style context is casual"""
        return self.formality_level <= 4
    
    def get_style_keywords(self) -> Set[str]:
        """Get keywords associated with the style context"""
        keywords = {self.primary_style.name.lower()}
        keywords.update(style.name.lower() for style in self.secondary_styles)
        return keywords 