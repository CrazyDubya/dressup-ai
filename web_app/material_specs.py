"""
Material specifications for outfit generation
"""
from dataclasses import dataclass
from typing import Set, Dict, Optional

@dataclass
class MaterialSpecifications:
    """Specifications for materials used in outfit generation"""
    name: str
    properties: Dict[str, str]
    care_instructions: Set[str]
    seasonal_suitability: Set[str]
    weight: Optional[float] = None  # in g/m²
    stretch: Optional[float] = None  # percentage
    breathability: Optional[int] = None  # 1-10 scale
    durability: Optional[int] = None  # 1-10 scale
    cost_per_meter: Optional[float] = None
    
    def is_suitable_for_season(self, season: str) -> bool:
        """Check if material is suitable for given season"""
        return season.lower() in {s.lower() for s in self.seasonal_suitability}
    
    def get_care_instructions(self) -> str:
        """Get formatted care instructions"""
        return "\n".join(sorted(self.care_instructions)) 