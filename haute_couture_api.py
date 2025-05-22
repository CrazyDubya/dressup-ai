from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import List, Optional, Dict, Union, Any, Annotated
import random
import logging
import time
from datetime import datetime
from material_specs import MaterialSpecifications

app = FastAPI(title="Haute Couture Outfit Generator",
             description="Specialized API for generating high-end, custom-made fashion outfits",
             version="1.0.0")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('haute_couture.log')
    ]
)
logger = logging.getLogger(__name__)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize material specifications
material_specs = MaterialSpecifications()

# Haute couture materials
HAUTE_COUTURE_MATERIALS = {
    'luxury_fabrics': {
        'silk': {
            'types': ['charmeuse', 'chiffon', 'dupioni', 'organza', 'taffeta'],
            'properties': ['lustrous', 'smooth', 'flowing'],
            'usage': ['formal wear', 'evening wear', 'bridal'],
            'color': {
                'primary': 'ivory',
                'metallic': True,
                'opacity': 0.9,
                'light_reflection': 'high'
            },
            'texture': {
                'type': 'smooth',
                'surface_finish': 'lustrous'
            },
            'physical': {
                'weight': 80,
                'thickness': 0.15,
                'stretch': 5,
                'drape': 'flowing',
                'breathability': 8
            },
            'care': {
                'washing': 'dry clean only',
                'drying': 'lay flat',
                'ironing': 'low heat',
                'dry_cleaning': True
            }
        },
        'lace': {
            'types': ['chantilly', 'alencon', 'guipure', 'corded', 'embroidered'],
            'properties': ['delicate', 'intricate', 'romantic'],
            'usage': ['formal wear', 'bridal', 'evening wear'],
            'color': {
                'primary': 'ivory',
                'opacity': 0.8,
                'light_reflection': 'medium'
            },
            'texture': {
                'type': 'patterned',
                'pattern': 'floral',
                'embossed': True
            },
            'physical': {
                'weight': 150,
                'thickness': 0.5,
                'stretch': 10,
                'drape': 'structured',
                'breathability': 7
            },
            'care': {
                'washing': 'hand wash',
                'drying': 'lay flat',
                'ironing': 'low heat',
                'dry_cleaning': True
            }
        },
        'velvet': {
            'types': ['silk velvet', 'crushed velvet', 'panne velvet', 'stretch velvet'],
            'properties': ['plush', 'luxurious', 'rich'],
            'usage': ['formal wear', 'evening wear'],
            'color': {
                'primary': 'burgundy',
                'opacity': 1.0,
                'light_reflection': 'variable'
            },
            'texture': {
                'type': 'pile',
                'surface_finish': 'plush'
            },
            'physical': {
                'weight': 300,
                'thickness': 1.0,
                'stretch': 0,
                'drape': 'heavy',
                'breathability': 5
            },
            'care': {
                'washing': 'dry clean only',
                'drying': 'hang dry',
                'ironing': 'steam only',
                'dry_cleaning': True
            }
        },
        'brocade': {
            'types': ['silk brocade', 'metallic brocade', 'jacquard brocade'],
            'properties': ['ornate', 'structured', 'regal'],
            'usage': ['formal wear', 'evening wear'],
            'color': {
                'primary': 'gold',
                'metallic': True,
                'opacity': 1.0,
                'light_reflection': 'high'
            },
            'texture': {
                'type': 'raised pattern',
                'pattern': 'floral',
                'embossed': True
            },
            'physical': {
                'weight': 250,
                'thickness': 0.8,
                'stretch': 0,
                'drape': 'structured',
                'breathability': 6
            },
            'care': {
                'washing': 'dry clean only',
                'drying': 'lay flat',
                'ironing': 'press on reverse',
                'dry_cleaning': True
            }
        }
    }
}

# Event-specific silhouettes
EVENT_SILHOUETTES = {
    "gala": ["ball_gown", "mermaid", "a_line"],
    "bridal": ["ball_gown", "mermaid", "a_line", "sheath"],
    "fashion show": ["avant_garde", "sculptural", "architectural"],
    "opera": ["ball_gown", "mermaid", "a_line"],
    "garden party": ["a_line", "empire", "sheath"],
    "winter ball": ["ball_gown", "mermaid", "a_line"],
    "formal": ["ball_gown", "mermaid", "a_line", "sheath"]
}

# Silhouette options
SILHOUETTE_OPTIONS = {
    "ball_gown": {
        "description": "Full skirt with fitted bodice",
        "formality": "very formal",
        "occasions": ["gala", "wedding", "state dinner"],
        "complexity": 9
    },
    "mermaid": {
        "description": "Fitted through body with flared bottom",
        "formality": "formal",
        "occasions": ["gala", "wedding", "red carpet"],
        "complexity": 8
    },
    "a_line": {
        "description": "Fitted at top, gradually widens",
        "formality": "versatile",
        "occasions": ["gala", "wedding", "formal event"],
        "complexity": 7
    },
    "sheath": {
        "description": "Straight cut, follows body line",
        "formality": "semi-formal",
        "occasions": ["cocktail", "formal dinner"],
        "complexity": 6
    },
    "empire": {
        "description": "High waistline, flowing skirt",
        "formality": "semi-formal",
        "occasions": ["garden party", "summer event"],
        "complexity": 7
    },
    "avant_garde": {
        "description": "Experimental, artistic design",
        "formality": "special",
        "occasions": ["fashion show", "art event"],
        "complexity": 10
    },
    "sculptural": {
        "description": "Architectural, structured design",
        "formality": "special",
        "occasions": ["fashion show", "art event"],
        "complexity": 9
    },
    "architectural": {
        "description": "Geometric, structured design",
        "formality": "special",
        "occasions": ["fashion show", "art event"],
        "complexity": 9
    }
}

# Silhouette complexity levels
SILHOUETTE_COMPLEXITY = {
    'low': 3,
    'medium': 5,
    'high': 7,
    'very high': 9
}

# Construction details
CONSTRUCTION_DETAILS = {
    "hand_sewing": {
        "description": "Traditional hand-sewing techniques",
        "estimated_time": 20,
        "complexity": "high",
        "required_skills": ["precision", "patience"],
        "tools": ["needles", "thread", "scissors"]
    },
    "draping": {
        "description": "Fabric manipulation on dress form",
        "estimated_time": 15,
        "complexity": "medium",
        "required_skills": ["spatial awareness", "fabric knowledge"],
        "tools": ["dress form", "pins", "muslin"]
    },
    "pleating": {
        "description": "Creating regular folds in fabric",
        "estimated_time": 10,
        "complexity": "medium",
        "required_skills": ["precision", "pattern making"],
        "tools": ["pleating board", "iron", "pins"]
    },
    "boning": {
        "description": "Adding structure with rigid materials",
        "estimated_time": 12,
        "complexity": "high",
        "required_skills": ["structural knowledge", "precision"],
        "tools": ["boning", "casing", "pliers"]
    },
    "beading": {
        "description": "Adding decorative beads and sequins",
        "estimated_time": 25,
        "complexity": "very high",
        "required_skills": ["detail oriented", "hand sewing"],
        "tools": ["beading needle", "beads", "thread"]
    },
    "embroidery": {
        "description": "Decorative needlework",
        "estimated_time": 30,
        "complexity": "very high",
        "required_skills": ["artistic ability", "hand sewing"],
        "tools": ["embroidery hoop", "thread", "needles"]
    },
    "laser_cutting": {
        "description": "Precision cutting with laser",
        "estimated_time": 8,
        "complexity": "medium",
        "required_skills": ["digital design", "machine operation"],
        "tools": ["laser cutter", "computer", "design software"]
    },
    "3d_printing": {
        "description": "Creating 3D elements",
        "estimated_time": 10,
        "complexity": "high",
        "required_skills": ["3D modeling", "machine operation"],
        "tools": ["3D printer", "computer", "design software"]
    }
}

SILHOUETTES = {
    'ball_gown': {
        'description': 'Full skirt with fitted bodice',
        'suitable_for': ['evening wear', 'bridal', 'formal events'],
        'complexity': 9
    },
    'mermaid': {
        'description': 'Fitted through the body, flaring at the knee',
        'suitable_for': ['evening wear', 'formal events'],
        'complexity': 8
    },
    'a_line': {
        'description': 'Fitted at the top, gradually widening to the hem',
        'suitable_for': ['all occasions'],
        'complexity': 7
    },
    'sheath': {
        'description': 'Straight, body-hugging silhouette',
        'suitable_for': ['evening wear', 'formal events'],
        'complexity': 6
    },
    'empire': {
        'description': 'High-waisted silhouette with flowing skirt',
        'suitable_for': ['evening wear', 'garden parties'],
        'complexity': 7
    },
    'column': {
        'description': 'Straight and narrow from shoulder to hem',
        'suitable_for': ['evening wear', 'formal events'],
        'complexity': 6
    },
    'trumpet': {
        'description': 'Fitted through mid-thigh, flaring to hem',
        'suitable_for': ['evening wear', 'formal events'],
        'complexity': 8
    },
    'fit_and_flare': {
        'description': 'Fitted bodice with flared skirt',
        'suitable_for': ['evening wear', 'cocktail parties'],
        'complexity': 7
    }
}

CONSTRUCTION_TECHNIQUES = {
    'hand_sewing': {
        'description': 'Traditional hand-sewing techniques',
        'complexity': 10,
        'time_estimate': 'high'
    },
    'boning': {
        'description': 'Structural support using boning',
        'complexity': 9,
        'time_estimate': 'high'
    },
    'draping': {
        'description': 'Fabric manipulation and draping',
        'complexity': 8,
        'time_estimate': 'medium'
    },
    'pleating': {
        'description': 'Complex pleating techniques',
        'complexity': 7,
        'time_estimate': 'medium'
    }
}

# Haute Couture specific models
class HauteCoutureProfile(BaseModel):
    """Enhanced client profile for haute couture design."""
    client_name: str
    measurements: Dict[str, float]
    style_preferences: List[str] = Field(default_factory=list)
    color_preferences: List[str] = Field(default_factory=list)
    fabric_preferences: List[str] = Field(default_factory=list)
    special_requirements: List[str] = Field(default_factory=list)
    event_details: Dict[str, str]
    budget_range: str
    timeline: str

    @field_validator('style_preferences', 'color_preferences', 'fabric_preferences', 'special_requirements')
    @classmethod
    def validate_list_fields(cls, v):
        """Validate that list fields are properly formatted."""
        if v is None:
            return []
        elif isinstance(v, str):
            return [v]
        return v

    @field_validator('measurements')
    @classmethod
    def validate_measurements(cls, v):
        """Validate measurements."""
        required_measurements = {'height', 'bust', 'waist', 'hips', 'shoulder_width'}
        missing = required_measurements - set(v.keys())
        if missing:
            raise ValueError(f"Missing required measurements: {missing}")
        return v

    @field_validator('budget_range')
    @classmethod
    def validate_budget_range(cls, v):
        """Validate budget range."""
        valid_ranges = ['luxury', 'premium', 'high-end']
        if v.lower() not in [r.lower() for r in valid_ranges]:
            raise ValueError(f"Invalid budget range: {v}. Must be one of {valid_ranges}")
        return v.lower()

    @field_validator('event_details')
    @classmethod
    def validate_event_details(cls, v):
        """Validate event details."""
        required_details = {'type', 'time', 'venue', 'season'}
        missing = required_details - set(v.keys())
        if missing:
            raise ValueError(f"Missing required event details: {missing}")
        return v

class ColorSpec(BaseModel):
    """Color specification model."""
    primary: str
    secondary: Optional[str] = None
    accent: Optional[str] = None
    metallic: bool = False
    iridescent: bool = False
    opacity: float = 1.0
    light_reflection: Optional[str] = None

class TextureSpec(BaseModel):
    """Texture specification model."""
    type: str
    pattern: Optional[str] = None
    pattern_scale: Optional[str] = None
    embossed: bool = False
    quilted: bool = False
    surface_finish: Optional[str] = None

class PhysicalProperties(BaseModel):
    """Physical properties model."""
    weight: float  # g/m²
    thickness: float  # mm
    stretch: float  # percentage
    drape: str
    breathability: int  # 1-10
    thermal_properties: Optional[str] = None
    sound: Optional[str] = None

class SustainabilityInfo(BaseModel):
    """Sustainability information model."""
    eco_friendly: bool = False
    biodegradable: bool = False
    recycled_content: Optional[float] = None  # percentage
    certifications: Optional[List[str]] = Field(default_factory=list)
    water_usage: Optional[float] = None  # liters per kg
    carbon_footprint: Optional[float] = None  # kg CO2 per kg
    notes: Optional[str] = None

class CareInstructions(BaseModel):
    """Care instructions model."""
    washing: str
    drying: str
    ironing: str
    dry_cleaning: bool = False
    special_care: Optional[str] = None
    storage: Optional[str] = None

class DigitalProperties(BaseModel):
    """Digital properties for rendering."""
    texture_map: Optional[str] = None
    normal_map: Optional[str] = None
    roughness_map: Optional[str] = None
    metallic_map: Optional[str] = None
    displacement_map: Optional[str] = None
    render_settings: Optional[Dict[str, Any]] = None

class MaterialDetail(BaseModel):
    """Enhanced material detail model with comprehensive properties."""
    # Core properties (existing)
    type: str
    specific_type: str
    properties: List[str] = []
    usage: str
    
    # New detailed specifications
    color: Optional[ColorSpec] = None
    texture: Optional[TextureSpec] = None
    physical: Optional[PhysicalProperties] = None
    sustainability: Optional[SustainabilityInfo] = None
    care: Optional[CareInstructions] = None
    digital: Optional[DigitalProperties] = None
    
    # Additional properties
    finish: Optional[str] = None  # waterproof, stain-resistant, etc.
    construction_notes: Optional[str] = None
    quality_grade: Optional[str] = None
    seasonal_suitability: Optional[List[str]] = None
    durability: Optional[int] = None  # 1-10
    
    # Custom/experimental properties
    extra: Optional[Dict[str, Any]] = None

    @classmethod
    def from_fabric_details(cls, fabric_type: str, fabric_details: dict, specific_type: str, usage: str):
        """Create a MaterialDetail instance from fabric details with enhanced properties."""
        try:
            logger.debug(f"Creating MaterialDetail for {fabric_type} with details: {fabric_details}")
            
            # Handle properties safely
            props = fabric_details.get('properties', [])
            if isinstance(props, str):
                props = [p.strip() for p in props.split(',')]
            elif not isinstance(props, list):
                props = ['elegant']
            logger.debug(f"Processed properties: {props}")
            
            # Extract color information
            color_spec = None
            if 'color' in fabric_details:
                try:
                    color_spec = ColorSpec(**fabric_details['color'])
                    logger.debug(f"Created color spec: {color_spec}")
                except Exception as e:
                    logger.warning(f"Error creating color spec: {str(e)}")
            
            # Extract texture information
            texture_spec = None
            if 'texture' in fabric_details:
                try:
                    texture_spec = TextureSpec(**fabric_details['texture'])
                    logger.debug(f"Created texture spec: {texture_spec}")
                except Exception as e:
                    logger.warning(f"Error creating texture spec: {str(e)}")
            
            # Extract physical properties
            physical_props = None
            if 'physical' in fabric_details:
                try:
                    physical_props = PhysicalProperties(**fabric_details['physical'])
                    logger.debug(f"Created physical properties: {physical_props}")
                except Exception as e:
                    logger.warning(f"Error creating physical properties: {str(e)}")
            
            # Extract sustainability information
            sustainability_info = None
            if 'sustainability' in fabric_details:
                try:
                    sustainability_info = SustainabilityInfo(**fabric_details['sustainability'])
                    logger.debug(f"Created sustainability info: {sustainability_info}")
                except Exception as e:
                    logger.warning(f"Error creating sustainability info: {str(e)}")
            
            # Extract care instructions
            care_info = None
            if 'care' in fabric_details:
                try:
                    care_info = CareInstructions(**fabric_details['care'])
                    logger.debug(f"Created care instructions: {care_info}")
                except Exception as e:
                    logger.warning(f"Error creating care instructions: {str(e)}")
            
            # Extract digital properties
            digital_props = None
            if 'digital' in fabric_details:
                try:
                    digital_props = DigitalProperties(**fabric_details['digital'])
                    logger.debug(f"Created digital properties: {digital_props}")
                except Exception as e:
                    logger.warning(f"Error creating digital properties: {str(e)}")
            
            material = cls(
                type=fabric_type,
                specific_type=specific_type,
                properties=props,
                usage=usage,
                color=color_spec,
                texture=texture_spec,
                physical=physical_props,
                sustainability=sustainability_info,
                care=care_info,
                digital=digital_props,
                finish=fabric_details.get('finish'),
                construction_notes=fabric_details.get('construction_notes'),
                quality_grade=fabric_details.get('quality_grade'),
                seasonal_suitability=fabric_details.get('seasonal_suitability'),
                durability=fabric_details.get('durability'),
                extra=fabric_details.get('extra')
            )
            logger.debug(f"Successfully created MaterialDetail: {material}")
            return material
        except Exception as e:
            logger.error(f"Error creating MaterialDetail: {str(e)}")
            logger.error("Traceback:", exc_info=True)
            raise

class FabricCombination(BaseModel):
    """Enhanced fabric combination model."""
    type: str
    specific_type: str
    usage: str
    properties: List[str] = Field(default_factory=list)
    color: Optional[ColorSpec] = None
    texture: Optional[TextureSpec] = None
    physical: Optional[PhysicalProperties] = None
    sustainability: Optional[SustainabilityInfo] = None
    care: Optional[CareInstructions] = None
    digital: Optional[DigitalProperties] = None
    extra: Optional[Dict[str, Any]] = None

    @field_validator('properties')
    @classmethod
    def validate_properties(cls, v):
        """Validate that properties are properly formatted."""
        if not v:
            return ['elegant']
        if isinstance(v, str):
            return [p.strip() for p in v.split(',')]
        if isinstance(v, list):
            return [str(p).strip() for p in v]
        return ['elegant']

    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        """Validate fabric type."""
        if v not in HAUTE_COUTURE_MATERIALS.get('luxury_fabrics', {}):
            raise ValueError(f"Invalid fabric type: {v}")
        return v

    @field_validator('specific_type')
    @classmethod
    def validate_specific_type(cls, v, values):
        """Validate specific fabric type."""
        if 'type' in values:
            fabric_type = values['type']
            fabric_details = HAUTE_COUTURE_MATERIALS.get('luxury_fabrics', {}).get(fabric_type, {})
            valid_types = fabric_details.get('types', [])
            if v not in valid_types:
                raise ValueError(f"Invalid specific type: {v} for fabric type: {fabric_type}")
        return v

    @field_validator('usage')
    @classmethod
    def validate_usage(cls, v, values):
        """Validate usage."""
        if 'type' in values:
            fabric_type = values['type']
            fabric_details = HAUTE_COUTURE_MATERIALS.get('luxury_fabrics', {}).get(fabric_type, {})
            valid_usage = fabric_details.get('usage', [])
            if isinstance(valid_usage, str):
                valid_usage = [valid_usage]
            if v not in valid_usage:
                raise ValueError(f"Invalid usage: {v} for fabric type: {fabric_type}")
        return v

class HauteCoutureDesign(BaseModel):
    """Enhanced haute couture design model."""
    design_name: str
    silhouette: str
    fabric_combinations: List[FabricCombination] = Field(default_factory=list)
    construction_techniques: List[str] = Field(default_factory=list)
    complexity_level: str
    estimated_hours: int
    design_notes: Optional[str] = None
    inspiration_references: Optional[List[str]] = Field(default_factory=list)
    seasonal_considerations: Optional[List[str]] = Field(default_factory=list)
    sustainability_notes: Optional[str] = None

    @field_validator('fabric_combinations', 'construction_techniques', 'inspiration_references', 'seasonal_considerations')
    @classmethod
    def validate_list_fields(cls, v):
        """Validate that list fields are properly formatted."""
        if v is None:
            return []
        return v

    @field_validator('silhouette')
    @classmethod
    def validate_silhouette(cls, v):
        """Validate silhouette value."""
        if v not in SILHOUETTE_OPTIONS:
            raise ValueError(f"Invalid silhouette: {v}. Must be one of {list(SILHOUETTE_OPTIONS.keys())}")
        return v

    @field_validator('complexity_level')
    @classmethod
    def validate_complexity_level(cls, v):
        """Validate complexity level."""
        valid_levels = ['low', 'medium', 'high', 'very high']
        if v not in valid_levels:
            raise ValueError(f"Invalid complexity level: {v}. Must be one of {valid_levels}")
        return v

    @field_validator('estimated_hours')
    @classmethod
    def validate_estimated_hours(cls, v):
        """Validate estimated hours."""
        if v < 0:
            raise ValueError("Estimated hours cannot be negative")
        return v

class MaterialCost(BaseModel):
    """Model for material cost calculation."""
    fabric_type: str
    specific_type: str
    base_cost: float
    quality_multiplier: float
    complexity_multiplier: float
    total_cost: float

class HauteCoutureOutfit(BaseModel):
    """Enhanced haute couture outfit model."""
    design_concept: HauteCoutureDesign
    materials: List[MaterialDetail] = Field(default_factory=list)
    material_costs: List[MaterialCost] = Field(default_factory=list)
    construction_techniques: List[str] = Field(default_factory=list)
    quality_control: List[str] = Field(default_factory=list)
    estimated_completion_time: str
    sustainability_impact: Optional[Dict[str, Any]] = None
    digital_rendering: Optional[Dict[str, Any]] = None

    @field_validator('materials', 'material_costs', 'construction_techniques', 'quality_control')
    @classmethod
    def validate_list_fields(cls, v):
        """Validate that list fields are properly formatted."""
        if v is None:
            return []
        return v

class HauteCoutureOutfitResponse(BaseModel):
    """Response model for a generated haute couture outfit."""
    design: Optional[HauteCoutureDesign] = None
    materials: Optional[List[MaterialDetail]] = Field(default_factory=list)
    material_costs: Optional[List[MaterialCost]] = Field(default_factory=list)
    construction_notes: Optional[List[str]] = Field(default_factory=list)
    embellishment_details: Optional[Dict[str, Any]] = None
    estimated_cost: Optional[float] = None
    timeline: Optional[str] = None
    special_instructions: Optional[List[str]] = Field(default_factory=list)
    avant_garde_details: Optional[Dict[str, Any]] = None
    quality_control_points: Optional[List[str]] = Field(default_factory=list)

    @field_validator('materials', 'material_costs', 'construction_notes', 'special_instructions', 'quality_control_points')
    @classmethod
    def validate_list_fields(cls, v):
        """Validate that list fields are properly formatted."""
        if v is None:
            return []
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "design": {
                    "design_name": "HC_Example_20240502",
                    "inspiration": "Custom design",
                    "silhouette": "ball_gown",
                    "fabric_combinations": [
                        {
                            "type": "silk",
                            "specific_type": "duchesse",
                            "usage": "evening wear"
                        }
                    ],
                    "construction_techniques": ["hand_sewing", "draping"],
                    "estimated_hours": 80,
                    "complexity_level": 9
                },
                "materials": [
                    {
                        "type": "silk",
                        "specific_type": "duchesse",
                        "properties": "lustrous, flowing, elegant",
                        "usage": "evening wear"
                    }
                ],
                "material_costs": [
                    {
                        "fabric_type": "silk",
                        "specific_type": "duchesse",
                        "base_cost": 1000,
                        "quality_multiplier": 1.5,
                        "complexity_multiplier": 1.2,
                        "total_cost": 1800
                    }
                ],
                "construction_notes": [
                    "hand_sewing: Traditional hand-sewing techniques - Estimated time: high"
                ],
                "estimated_cost": 10000.0,
                "timeline": "Estimated completion time: 80 hours",
                "quality_control_points": [
                    "Fabric quality and authenticity verification",
                    "Precise measurements and fit check",
                    "Construction technique inspection",
                    "Final garment inspection"
                ]
            }
        }
    }

# Construction time estimates
CONSTRUCTION_TIME_ESTIMATES = {
    "hand_sewing": "high",
    "draping": "medium",
    "pleating": "medium",
    "boning": "high",
    "beading": "very high",
    "embroidery": "very high",
    "laser_cutting": "medium",
    "3d_printing": "high"
}

def convert_properties_to_string(properties: Union[List[str], str]) -> str:
    """Convert properties to string format."""
    if isinstance(properties, list):
        return ', '.join(properties)
    return properties

@app.post("/api/haute-couture/design", response_model=HauteCoutureDesign)
async def create_haute_couture_design(profile: HauteCoutureProfile):
    """Create a custom haute couture design based on client profile."""
    try:
        logger.debug("Starting design creation with profile: %s", profile.dict())
        
        # Generate design name
        design_name = f"{profile.client_name}'s {datetime.now().strftime('%Y')} Collection"
        logger.debug("Generated design name: %s", design_name)
        
        # Select silhouette based on style preferences and event type
        logger.debug("SILHOUETTE_OPTIONS: %s", SILHOUETTE_OPTIONS)
        if not SILHOUETTE_OPTIONS:
            logger.error("SILHOUETTE_OPTIONS is empty")
            raise HTTPException(status_code=500, detail="No silhouette options available")
        
        # Get event type from event details
        event_type = profile.event_details.get('type', 'formal').lower()
        logger.debug("Event type: %s", event_type)
        
        # Select silhouette based on event type and style preferences
        try:
            logger.debug("Selecting silhouette with style_preferences: %s, event_type: %s", profile.style_preferences, event_type)
            silhouette = select_silhouette(profile.style_preferences, event_type)
            logger.debug("Selected silhouette: %s", silhouette)
        except Exception as e:
            logger.warning(f"Error selecting silhouette: {str(e)}, using default")
            silhouette = "ball_gown"  # Default to ball gown if selection fails
        
        # Validate fabric preferences
        valid_fabrics = []
        logger.debug("Fabric preferences: %s", profile.fabric_preferences)
        logger.debug("HAUTE_COUTURE_MATERIALS: %s", HAUTE_COUTURE_MATERIALS)
        
        luxury_fabrics = HAUTE_COUTURE_MATERIALS.get('luxury_fabrics', {})
        for fabric in profile.fabric_preferences:
            logger.debug("Checking fabric: %s", fabric)
            if fabric in luxury_fabrics:
                valid_fabrics.append(fabric)
        
        logger.debug("Valid fabrics: %s", valid_fabrics)
        if not valid_fabrics:
            logger.debug("No valid fabrics found, defaulting to silk")
            valid_fabrics = ['silk']
        
        # Create fabric combinations
        fabric_combinations = []
        for fabric_type in valid_fabrics:
            try:
                logger.debug("Processing fabric type: %s", fabric_type)
                fabric_detail = luxury_fabrics.get(fabric_type)
                logger.debug("Fabric detail: %s", fabric_detail)
                
                if not fabric_detail:
                    logger.warning(f"Invalid fabric detail for {fabric_type}")
                    continue
                
                # Get fabric types safely
                fabric_types = fabric_detail.get('types', [])
                if not fabric_types:
                    logger.warning(f"No types available for {fabric_type}")
                    continue
                
                specific_type = random.choice(fabric_types)
                logger.debug("Selected specific type: %s", specific_type)
                
                # Handle usage field safely
                usage_list = fabric_detail.get('usage', ['formal wear'])
                if isinstance(usage_list, str):
                    usage_list = [usage_list]
                usage = usage_list[0] if usage_list else 'formal wear'
                logger.debug("Selected usage: %s", usage)
                
                # Handle properties field safely
                properties = fabric_detail.get('properties', ['elegant'])
                logger.debug("Raw properties: %s", properties)
                if isinstance(properties, str):
                    properties = [p.strip() for p in properties.split(',')]
                elif isinstance(properties, list):
                    properties = [str(p).strip() for p in properties]
                else:
                    properties = ['elegant']
                logger.debug("Final properties: %s", properties)
                
                # Create color spec safely
                color_spec = None
                if 'color' in fabric_detail:
                    try:
                        color_spec = ColorSpec(**fabric_detail['color'])
                        logger.debug("Created color spec: %s", color_spec)
                    except Exception as e:
                        logger.warning(f"Error creating color spec: {str(e)}")
                
                # Create texture spec safely
                texture_spec = None
                if 'texture' in fabric_detail:
                    try:
                        texture_spec = TextureSpec(**fabric_detail['texture'])
                        logger.debug("Created texture spec: %s", texture_spec)
                    except Exception as e:
                        logger.warning(f"Error creating texture spec: {str(e)}")
                
                # Create physical properties safely
                physical_props = None
                if 'physical' in fabric_detail:
                    try:
                        physical_props = PhysicalProperties(**fabric_detail['physical'])
                        logger.debug("Created physical properties: %s", physical_props)
                    except Exception as e:
                        logger.warning(f"Error creating physical properties: {str(e)}")
                
                # Create sustainability info safely
                sustainability_info = None
                if 'sustainability' in fabric_detail:
                    try:
                        sustainability_info = SustainabilityInfo(**fabric_detail['sustainability'])
                        logger.debug("Created sustainability info: %s", sustainability_info)
                    except Exception as e:
                        logger.warning(f"Error creating sustainability info: {str(e)}")
                
                # Create care instructions safely
                care_instructions = None
                if 'care' in fabric_detail:
                    try:
                        care_instructions = CareInstructions(**fabric_detail['care'])
                        logger.debug("Created care instructions: %s", care_instructions)
                    except Exception as e:
                        logger.warning(f"Error creating care instructions: {str(e)}")
                
                # Create digital properties safely
                digital_props = None
                if 'digital' in fabric_detail:
                    try:
                        digital_props = DigitalProperties(**fabric_detail['digital'])
                        logger.debug("Created digital properties: %s", digital_props)
                    except Exception as e:
                        logger.warning(f"Error creating digital properties: {str(e)}")
                
                # Create fabric combination
                fabric_combination = FabricCombination(
                    type=fabric_type,
                    specific_type=specific_type,
                    usage=usage,
                    properties=properties,
                    color=color_spec,
                    texture=texture_spec,
                    physical=physical_props,
                    sustainability=sustainability_info,
                    care=care_instructions,
                    digital=digital_props
                )
                logger.debug("Created fabric combination: %s", fabric_combination)
                fabric_combinations.append(fabric_combination)
                
            except Exception as e:
                logger.warning(f"Error processing fabric {fabric_type}: {str(e)}")
                continue
        
        logger.debug("Final fabric combinations: %s", fabric_combinations)
        
        # Select construction techniques
        try:
            logger.debug("Selecting construction techniques for silhouette: %s", silhouette)
            construction_techniques = select_construction_techniques(silhouette, profile.style_preferences)
            logger.debug("Selected construction techniques: %s", construction_techniques)
        except Exception as e:
            logger.warning(f"Error selecting construction techniques: {str(e)}, using defaults")
            construction_techniques = ["hand_sewing", "draping"]
        
        # Calculate complexity
        try:
            logger.debug("Calculating complexity for silhouette: %s and techniques: %s", silhouette, construction_techniques)
            complexity = calculate_complexity(silhouette, construction_techniques)
            logger.debug("Calculated complexity: %s", complexity)
        except Exception as e:
            logger.warning(f"Error calculating complexity: {str(e)}, using default")
            complexity = "medium"
        
        # Calculate estimated hours
        try:
            logger.debug("Calculating estimated hours for complexity: %s", complexity)
            estimated_hours = calculate_estimated_hours(complexity)
            logger.debug("Calculated estimated hours: %s", estimated_hours)
        except Exception as e:
            logger.warning(f"Error calculating estimated hours: {str(e)}, using default")
            estimated_hours = 80
        
        # Create design
        design = HauteCoutureDesign(
            design_name=design_name,
            silhouette=silhouette,
            fabric_combinations=fabric_combinations,
            construction_techniques=construction_techniques,
            complexity_level=complexity,
            estimated_hours=estimated_hours
        )
        logger.debug("Created design: %s", design)
        
        return design
        
    except Exception as e:
        logger.error(f"Error creating haute couture design: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/haute-couture/outfit", response_model=HauteCoutureOutfit)
async def generate_haute_couture_outfit(profile: HauteCoutureProfile):
    """Generate a complete haute couture outfit based on client profile."""
    try:
        logger.debug("Starting outfit generation with profile: %s", profile.dict())
        
        # First create the design
        try:
            design = await create_haute_couture_design(profile)
            logger.debug("Successfully created design: %s", design)
        except Exception as e:
            logger.error(f"Error in create_haute_couture_design: {str(e)}")
            raise
        
        # Generate materials with enhanced properties
        materials = []
        material_costs = []
        
        logger.debug("Processing fabric combinations: %s", design.fabric_combinations)
        for fabric_combo in design.fabric_combinations:
            try:
                logger.debug("Processing fabric combination: %s", fabric_combo)
                fabric_detail = HAUTE_COUTURE_MATERIALS['luxury_fabrics'].get(fabric_combo.type)
                if not fabric_detail:
                    logger.warning(f"Fabric type {fabric_combo.type} not found in specifications")
                    continue
                
                material = MaterialDetail.from_fabric_details(
                    fabric_type=fabric_combo.type,
                    fabric_details=fabric_detail,
                    specific_type=fabric_combo.specific_type,
                    usage=fabric_combo.usage
                )
                materials.append(material)
                
                # Calculate material costs
                base_cost = 1000  # Base cost in USD
                quality_multiplier = 1.5 if material.quality_grade == 'A+' else 1.2
                complexity_multiplier = 1.3 if design.complexity_level == 'high' else 1.0
                
                material_costs.append(MaterialCost(
                    fabric_type=material.type,
                    specific_type=material.specific_type,
                    base_cost=base_cost,
                    quality_multiplier=quality_multiplier,
                    complexity_multiplier=complexity_multiplier,
                    total_cost=base_cost * quality_multiplier * complexity_multiplier
                ))
            except Exception as e:
                logger.error(f"Error processing material for {fabric_combo.type}: {str(e)}")
                continue
        
        # If no materials were successfully created, use default silk
        if not materials:
            logger.warning("No materials created, using default silk")
            silk_detail = HAUTE_COUTURE_MATERIALS['luxury_fabrics']['silk']
            materials.append(MaterialDetail.from_fabric_details(
                fabric_type='silk',
                fabric_details=silk_detail,
                specific_type='charmeuse',
                usage='dresses'
            ))
            material_costs.append(MaterialCost(
                fabric_type='silk',
                specific_type='charmeuse',
                base_cost=1000,
                quality_multiplier=1.5,
                complexity_multiplier=1.3,
                total_cost=1950
            ))
        
        # Generate construction notes
        construction_notes = []
        for technique in design.construction_techniques:
            if technique in CONSTRUCTION_DETAILS:
                construction_notes.append(CONSTRUCTION_DETAILS[technique]['description'])
        
        # Generate quality control points
        quality_control = [
            "Precise pattern matching",
            "Perfect seam alignment",
            "Impeccable hand-finishing",
            "Fabric grain alignment",
            "Drape verification",
            "Fit assessment",
            "Quality of hand-stitching",
            "Embellishment placement",
            "Overall balance and proportion"
        ]
        
        try:
            outfit = HauteCoutureOutfit(
                design_concept=design,
                materials=materials,
                material_costs=material_costs,
                construction_techniques=construction_notes,
                quality_control=quality_control,
                estimated_completion_time=f"{design.estimated_hours} hours",
                sustainability_impact={
                    "materials": [m.sustainability.dict() for m in materials if m.sustainability],
                    "certifications": list(set(
                        cert for m in materials 
                        if m.sustainability and m.sustainability.certifications 
                        for cert in m.sustainability.certifications
                    ))
                },
                digital_rendering={
                    "available_views": ["front", "back", "side", "detail"],
                    "material_swatches": [m.digital.dict() for m in materials if m.digital]
                }
            )
            logger.debug("Successfully created outfit: %s", outfit)
            return outfit
        except Exception as e:
            logger.error(f"Error creating outfit object: {str(e)}")
            raise
    except Exception as e:
        logger.error(f"Error generating haute couture outfit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/haute-couture/materials")
async def get_haute_couture_materials():
    """Get available haute couture materials."""
    return HAUTE_COUTURE_MATERIALS

@app.get("/api/haute-couture/silhouettes")
async def get_haute_couture_silhouettes():
    """Get available silhouettes."""
    return SILHOUETTES

@app.get("/api/haute-couture/techniques")
async def get_haute_couture_techniques():
    """Get available construction techniques."""
    return CONSTRUCTION_TECHNIQUES

def select_silhouette(style_preferences: List[str], event_type: str) -> str:
    """Select appropriate silhouette based on style preferences and event type."""
    try:
        # Map similar event types
        event_type = event_type.lower()
        logger.debug("Original event type: %s", event_type)
        
        if "gala" in event_type:
            event_type = "gala"
        elif "bridal" in event_type or "wedding" in event_type:
            event_type = "bridal"
        elif "fashion show" in event_type or "runway" in event_type:
            event_type = "fashion show"
        elif "opera" in event_type:
            event_type = "opera"
        elif "garden" in event_type:
            event_type = "garden party"
        elif "ball" in event_type:
            event_type = "winter ball"
        else:
            event_type = "formal"
        
        logger.debug("Mapped event type: %s", event_type)
        logger.debug("EVENT_SILHOUETTES: %s", EVENT_SILHOUETTES)
        
        # Get silhouettes for event type, default to formal if not found
        silhouettes = EVENT_SILHOUETTES.get(event_type)
        logger.debug("Silhouettes for event type: %s", silhouettes)
        
        if not silhouettes:
            silhouettes = EVENT_SILHOUETTES.get("formal", [])
            logger.debug("Using formal silhouettes: %s", silhouettes)
        
        # Check style preferences for specific silhouettes
        if style_preferences:
            logger.debug("Checking style preferences: %s", style_preferences)
            for pref in style_preferences:
                pref = pref.lower()
                logger.debug("Checking preference: %s", pref)
                if "avant-garde" in pref or "experimental" in pref:
                    return "avant_garde"
                elif "architectural" in pref:
                    return "architectural"
                elif "sculptural" in pref:
                    return "sculptural"
                elif "ball gown" in pref:
                    return "ball_gown"
                elif "mermaid" in pref:
                    return "mermaid"
                elif "a-line" in pref:
                    return "a_line"
                elif "sheath" in pref:
                    return "sheath"
                elif "empire" in pref:
                    return "empire"
                elif "column" in pref:
                    return "column"
        
        # If no specific preference matches, return first silhouette for event type
        # Make sure we have a valid silhouette
        if not silhouettes:
            logger.debug("No silhouettes available, using default")
            return "ball_gown"  # Default if no silhouettes available
        
        # Get the first silhouette from the list
        silhouette = silhouettes[0] if silhouettes else "ball_gown"
        logger.debug("Selected silhouette: %s", silhouette)
        return silhouette
        
    except Exception as e:
        logger.error(f"Error in select_silhouette: {str(e)}")
        logger.error("Traceback:", exc_info=True)
        return "ball_gown"  # Default if any error occurs

def generate_avant_garde_details(profile: HauteCoutureProfile) -> Dict[str, Any]:
    """Generate detailed specifications for avant-garde designs."""
    return {
        "concept": {
            "inspiration": "Architectural form meets organic movement",
            "artistic_direction": "Sculptural silhouettes with dynamic elements",
            "visual_impact": "Bold geometric shapes with fluid transitions"
        },
        "experimental_techniques": {
            "construction": [
                {
                    "name": "Heat molding",
                    "description": "Temperature-controlled precision molding",
                    "materials": ["neoprene", "technical fabrics"],
                    "complexity": "high"
                },
                {
                    "name": "Laser cutting",
                    "description": "Geometric patterns and precise detailing",
                    "materials": ["acrylic", "metallic mesh"],
                    "complexity": "high"
                }
            ],
            "surface_treatments": [
                {
                    "name": "3D printing",
                    "description": "Architectural elements and structural details",
                    "materials": ["biodegradable polymers", "metallic compounds"],
                    "complexity": "very high"
                }
            ]
        },
        "structural_elements": {
            "support_system": "Internal architectural framework",
            "movement_mechanics": "Kinetic elements with controlled flexibility",
            "balance_points": "Strategic weight distribution for dramatic silhouette"
        },
        "asymmetry_details": {
            "bodice": {
                "construction": "Geometric paneling with varied depths",
                "materials": "Layered technical fabrics with metallic mesh",
                "closure": "Hidden magnetic fastenings"
            },
            "skirt": {
                "construction": "Sculptural draping with architectural pleats",
                "materials": "Neoprene base with acrylic overlays",
                "movement": "Controlled volume with geometric voids"
            }
        },
        "sculptural_elements": [
            {
                "type": "Floating panels",
                "technique": "Cantilevered construction",
                "placement": "Asymmetric shoulder and hip"
            },
            {
                "type": "Geometric volumes",
                "technique": "Heat-molded structures",
                "placement": "Bodice and sleeve"
            }
        ],
        "innovative_closures": {
            "type": "Magnetic system",
            "placement": "Strategic points along asymmetric seams",
            "functionality": "Seamless transformation capability"
        },
        "lighting_integration": {
            "type": "Fiber optic elements",
            "placement": "Woven into metallic mesh panels",
            "effect": "Subtle illumination of sculptural elements"
        }
    }

def select_construction_techniques(silhouette: str, style_preferences: List[str]) -> List[str]:
    """Select appropriate construction techniques based on silhouette and style preferences."""
    available_techniques = list(CONSTRUCTION_DETAILS.keys())
    
    # Base techniques for each silhouette
    silhouette_techniques = {
        "ball_gown": ["boning", "pleating"],
        "mermaid": ["boning", "draping"],
        "sheath": ["draping", "hand_sewing"],
        "a_line": ["pleating", "hand_sewing"],
        "empire": ["draping", "hand_sewing"],
        "column": ["draping", "hand_sewing"],
        "trumpet": ["boning", "draping"],
        "fit_and_flare": ["pleating", "hand_sewing"]
    }
    
    # Get base techniques for silhouette
    techniques = silhouette_techniques.get(silhouette, ["hand_sewing", "draping"])
    
    # Add techniques based on style preferences
    if style_preferences:
        for pref in style_preferences:
            pref = pref.lower()
            if "ornate" in pref or "luxurious" in pref:
                if "beading" in available_techniques:
                    techniques.append("beading")
            elif "delicate" in pref or "feminine" in pref:
                if "embroidery" in available_techniques:
                    techniques.append("embroidery")
            elif "structured" in pref:
                if "boning" in available_techniques:
                    techniques.append("boning")
            elif "flowing" in pref or "draped" in pref:
                if "draping" in available_techniques:
                    techniques.append("draping")
    
    # Remove duplicates while preserving order
    seen = set()
    techniques = [x for x in techniques if not (x in seen or seen.add(x))]
    
    # Return first two techniques
    return techniques[:2]

def calculate_complexity(silhouette: str, techniques: List[str]) -> str:
    """Calculate the complexity level of a design based on silhouette and techniques."""
    logger.debug("Calculating complexity for silhouette: %s and techniques: %s", silhouette, techniques)
    logger.debug("SILHOUETTE_OPTIONS: %s", SILHOUETTE_OPTIONS)
    
    # Get base complexity from silhouette
    base_complexity = SILHOUETTE_OPTIONS.get(silhouette, {}).get('complexity', 5)
    logger.debug("Base complexity: %s", base_complexity)
    
    # Add complexity for each advanced technique
    technique_complexity = sum(2 for t in techniques if 'advanced' in t.lower())
    logger.debug("Technique complexity: %s", technique_complexity)
    
    # Calculate total complexity and cap it at 10
    total_complexity = min(base_complexity + technique_complexity, 10)
    logger.debug("Total complexity: %s", total_complexity)
    
    # Convert numeric complexity to string level
    if total_complexity >= 9:
        return 'very high'
    elif total_complexity >= 7:
        return 'high'
    elif total_complexity >= 5:
        return 'medium'
    else:
        return 'low'

def calculate_estimated_hours(complexity: str) -> int:
    """Calculate estimated hours based on complexity level."""
    # Base hours for each complexity level
    base_hours = {
        'low': 20,
        'medium': 80,
        'high': 120,
        'very high': 160
    }
    
    return base_hours.get(complexity, 80)

def calculate_estimated_cost(complexity: str, hours: int, num_materials: int) -> float:
    """Calculate estimated cost based on complexity, hours, and number of materials."""
    # Base cost per hour
    base_hourly_rate = 200
    
    # Complexity multiplier
    complexity_multiplier = 1 + (SILHOUETTE_COMPLEXITY.get(complexity, 5) / 10)
    
    # Material cost multiplier
    material_multiplier = 1 + (num_materials * 0.2)
    
    # Calculate total cost
    total_cost = base_hourly_rate * hours * complexity_multiplier * material_multiplier
    
    return round(total_cost, 2)

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host="127.0.0.1", port=5002, log_level="debug")
    except Exception as e:
        print(f"Error starting server: {str(e)}") 