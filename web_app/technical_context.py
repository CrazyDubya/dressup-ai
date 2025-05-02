"""
Technical context for outfit generation
"""
from dataclasses import dataclass
from typing import Dict, Set, Optional, List

@dataclass
class TechnicalContext:
    """Technical specifications for outfit generation"""
    construction_methods: Set[str]
    seam_types: Set[str]
    closures: Set[str]
    measurements: Dict[str, float]
    fit_preferences: Dict[str, str]
    alterations: Optional[List[str]] = None
    special_requirements: Optional[Dict[str, str]] = None
    
    def get_construction_details(self) -> Dict[str, str]:
        """Get detailed construction specifications"""
        return {
            'methods': sorted(list(self.construction_methods)),
            'seams': sorted(list(self.seam_types)),
            'closures': sorted(list(self.closures))
        }
    
    def requires_alterations(self) -> bool:
        """Check if outfit requires alterations"""
        return bool(self.alterations)
    
    def get_measurement_summary(self) -> str:
        """Get formatted measurement summary"""
        return "\n".join(f"{k}: {v}cm" for k, v in sorted(self.measurements.items())) 