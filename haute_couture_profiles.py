"""
Predefined haute couture profiles for different occasions and styles.
"""

from material_models import HauteCoutureProfile, MaterialDetail
from typing import Dict, List

HAUTE_COUTURE_PROFILES = {
    "evening_gala": HauteCoutureProfile(
        style_name="Evening Gala Gown",
        description="An elegant floor-length gown designed for formal evening events",
        recommended_materials=["silk", "satin", "velvet", "lace"],
        construction_techniques=[
            "Hand beading",
            "French seams",
            "Couture draping",
            "Internal corsetry",
            "Hand-rolled hems"
        ],
        silhouette="Fitted bodice with flowing A-line or mermaid skirt",
        details=[
            "Hand-sewn embellishments",
            "Built-in support structure",
            "Layered underskirts",
            "Hidden closures",
            "Optional train"
        ],
        timeline={
            "design_consultation": "1 week",
            "material_selection": "1 week",
            "pattern_making": "1 week",
            "construction": "4-6 weeks",
            "fittings": "3 sessions",
            "finishing": "1 week"
        },
        quality_control=[
            "Fabric quality inspection",
            "Draping assessment",
            "Fit verification",
            "Embellishment security check",
            "Movement test",
            "Final inspection"
        ]
    ),
    
    "bridal_couture": HauteCoutureProfile(
        style_name="Bridal Couture",
        description="A bespoke wedding gown combining tradition with personal style",
        recommended_materials=["silk", "lace", "tulle", "organza"],
        construction_techniques=[
            "Hand lace application",
            "Internal structure building",
            "Custom beading",
            "Precise draping",
            "Multiple layers construction"
        ],
        silhouette="Custom silhouette based on bride's preference",
        details=[
            "Hand-sewn lace appliqués",
            "Custom beading pattern",
            "Built-in corset",
            "Chapel or cathedral train",
            "Personalized embellishments"
        ],
        timeline={
            "design_consultation": "2 weeks",
            "material_selection": "2 weeks",
            "pattern_making": "2 weeks",
            "construction": "8-12 weeks",
            "fittings": "4-5 sessions",
            "finishing": "2 weeks"
        },
        quality_control=[
            "Material quality verification",
            "Construction technique review",
            "Fit assessment",
            "Movement evaluation",
            "Detail inspection",
            "Final verification"
        ]
    ),
    
    "spring_garden": HauteCoutureProfile(
        style_name="Spring Garden Party",
        description="A sophisticated yet playful ensemble for daytime events",
        recommended_materials=["silk", "cotton", "linen", "lace"],
        construction_techniques=[
            "Precision pleating",
            "Hand embroidery",
            "Delicate draping",
            "Light construction"
        ],
        silhouette="Fitted bodice with full or A-line skirt",
        details=[
            "Floral embellishments",
            "Delicate pleating",
            "Subtle beading",
            "Layered elements",
            "Hidden pockets"
        ],
        timeline={
            "design_consultation": "1 week",
            "material_selection": "1 week",
            "pattern_making": "1 week",
            "construction": "3-4 weeks",
            "fittings": "2-3 sessions",
            "finishing": "1 week"
        },
        quality_control=[
            "Fabric drape check",
            "Construction review",
            "Fit verification",
            "Movement assessment",
            "Detail inspection"
        ]
    ),
    
    "winter_ball": HauteCoutureProfile(
        style_name="Winter Ball Gown",
        description="A luxurious and opulent gown designed for winter formal events",
        recommended_materials=["velvet", "silk", "brocade", "fur"],
        construction_techniques=[
            "Heavy draping",
            "Layered construction",
            "Fur application",
            "Rich embellishments",
            "Structural support"
        ],
        silhouette="Full ball gown with dramatic volume",
        details=[
            "Rich fabric combinations",
            "Luxurious trims",
            "Dramatic train",
            "Built-in warmth",
            "Statement sleeves"
        ],
        timeline={
            "design_consultation": "2 weeks",
            "material_selection": "2 weeks",
            "pattern_making": "2 weeks",
            "construction": "6-8 weeks",
            "fittings": "4 sessions",
            "finishing": "2 weeks"
        },
        quality_control=[
            "Material weight check",
            "Warmth assessment",
            "Movement evaluation",
            "Embellishment security",
            "Final inspection"
        ]
    ),
    
    "opera_night": HauteCoutureProfile(
        style_name="Opera Night",
        description="An elegant and sophisticated ensemble for opera performances",
        recommended_materials=["silk", "velvet", "brocade", "lace"],
        construction_techniques=[
            "Precision tailoring",
            "Delicate draping",
            "Intricate beading",
            "Lace application",
            "Structural support"
        ],
        silhouette="Fitted bodice with dramatic skirt",
        details=[
            "Opera-length gloves",
            "Statement jewelry integration",
            "Dramatic train",
            "Rich embellishments",
            "Hidden pockets"
        ],
        timeline={
            "design_consultation": "2 weeks",
            "material_selection": "2 weeks",
            "pattern_making": "2 weeks",
            "construction": "6-8 weeks",
            "fittings": "4 sessions",
            "finishing": "2 weeks"
        },
        quality_control=[
            "Movement assessment",
            "Comfort evaluation",
            "Detail inspection",
            "Fit verification",
            "Final check"
        ]
    ),
    
    "avant_garde": HauteCoutureProfile(
        style_name="Avant-Garde Couture",
        description="A boundary-pushing design combining artistry with wearability",
        recommended_materials=["innovative textiles", "technical fabrics", "unusual combinations"],
        construction_techniques=[
            "Experimental construction",
            "Sculptural elements",
            "Mixed media application",
            "Technical innovation"
        ],
        silhouette="Architectural and innovative",
        details=[
            "Sculptural elements",
            "Unexpected closures",
            "Mixed media",
            "Technical features",
            "Artistic elements"
        ],
        timeline={
            "design_consultation": "2 weeks",
            "material_research": "2 weeks",
            "prototyping": "2 weeks",
            "construction": "6-8 weeks",
            "fittings": "3-4 sessions",
            "finishing": "2 weeks"
        },
        quality_control=[
            "Innovation assessment",
            "Wearability check",
            "Construction stability",
            "Movement evaluation",
            "Safety verification"
        ]
    )
}

def get_profile(profile_name: str) -> HauteCoutureProfile:
    """Get a haute couture profile by name."""
    if profile_name not in HAUTE_COUTURE_PROFILES:
        raise ValueError(f"Profile {profile_name} not found")
    return HAUTE_COUTURE_PROFILES[profile_name]

def list_profiles() -> List[str]:
    """Get a list of available profile names."""
    return list(HAUTE_COUTURE_PROFILES.keys())

def get_profile_details(profile_name: str) -> Dict:
    """Get detailed information about a profile."""
    profile = get_profile(profile_name)
    return {
        "name": profile.style_name,
        "description": profile.description,
        "materials": profile.recommended_materials,
        "techniques": profile.construction_techniques,
        "timeline": profile.timeline
    } 