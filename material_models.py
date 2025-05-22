from pydantic import BaseModel, Field
from typing import List, Optional

class MaterialDetail(BaseModel):
    """Detailed specifications for a material."""
    properties: str = Field(..., description="Comma-separated list of material properties")
    light_behavior: str = Field(..., description="Description of how the material interacts with light")
    draping: str = Field(..., description="Description of how the material drapes")
    surface_characteristics: List[str] = Field(..., description="List of surface characteristics")
    construction_notes: str = Field(..., description="Notes on construction techniques")
    care_instructions: str = Field(..., description="Care and maintenance instructions")

class TextureDetail(BaseModel):
    """Detailed specifications for a texture."""
    visual_properties: List[str] = Field(..., description="List of visual properties")
    light_interaction: str = Field(..., description="Description of how the texture interacts with light")
    movement_characteristics: str = Field(..., description="Description of movement characteristics")
    construction_notes: str = Field(..., description="Notes on construction techniques")
    care_instructions: str = Field(..., description="Care and maintenance instructions")

class FabricCombination(BaseModel):
    """Specifications for fabric combinations."""
    primary_material: str = Field(..., description="Primary material in the combination")
    secondary_material: Optional[str] = Field(None, description="Secondary material in the combination")
    recommended_use: str = Field(..., description="Recommended use cases for this combination")
    construction_notes: str = Field(..., description="Special construction considerations")
    care_instructions: str = Field(..., description="Combined care instructions")

class HauteCoutureProfile(BaseModel):
    """Profile for a haute couture design."""
    style_name: str = Field(..., description="Name of the style profile")
    description: str = Field(..., description="Detailed description of the style")
    recommended_materials: List[str] = Field(..., description="List of recommended materials")
    construction_techniques: List[str] = Field(..., description="List of construction techniques")
    silhouette: str = Field(..., description="Description of the silhouette")
    details: List[str] = Field(..., description="List of design details")
    timeline: dict = Field(..., description="Timeline breakdown for construction")
    quality_control: List[str] = Field(..., description="Quality control checkpoints")

class HauteCoutureDesign(BaseModel):
    """Complete haute couture design specification."""
    profile: HauteCoutureProfile
    materials: List[MaterialDetail]
    textures: List[TextureDetail]
    combinations: List[FabricCombination]
    measurements: dict
    timeline: dict
    cost_breakdown: dict
    special_requirements: Optional[List[str]] = None 