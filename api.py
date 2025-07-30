from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Dict, Union
import random
import json
from measurement_utils import MeasurementEstimator, BodyType, SpecialRequirement, MeasurementSystem
from measurement_validation import MeasurementValidation
from measurement_converter import MeasurementConverter
from material_models import MaterialDetail, TextureDetail, FabricCombination, HauteCoutureProfile, HauteCoutureDesign
from material_specs import MaterialSpecifications
from haute_couture_profiles import get_profile, list_profiles, get_profile_details
import logging
import time
from datetime import datetime
from measurement_endpoints import measurement_router

app = FastAPI()
app.include_router(measurement_router)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api.log')
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


class UserProfile(BaseModel):
    """User measurements and preferences."""
    height: Optional[float] = None
    weight: Optional[float] = None
    bust: Optional[float] = None
    waist: Optional[float] = None
    hips: Optional[float] = None
    inseam: Optional[float] = None
    shoe_size: Optional[float] = None
    comfort_level: Optional[int] = None
    style_preferences: Optional[List[str]] = None
    color_preferences: Optional[List[str]] = None
    fit_preferences: Optional[List[str]] = None
    special_requirement: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "UserProfile":
        return cls(**data)


class EventContext(BaseModel):
    """Event details and conditions."""
    event_type: Optional[str] = None
    formality_level: Optional[int] = None
    weather_conditions: Optional[List[str]] = None
    time_of_day: Optional[str] = None
    season: Optional[str] = None
    location: Optional[str] = None
    duration: Optional[int] = None
    activity_level: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "EventContext":
        return cls(**data)


# Initialize material specifications
material_specs = MaterialSpecifications()

# Basic material and legwear mappings for tests
MATERIAL_COMBINATIONS = {
    'summer': ['cotton', 'linen', 'silk', 'light', 'bamboo', 'modal', 'synthetic'],
    'winter': ['wool', 'cashmere', 'fleece', 'velvet', 'cotton', 'silk', 'synthetic'],
    'spring': ['cotton', 'linen', 'silk', 'light', 'synthetic', 'bamboo', 'modal'],
    'fall': ['wool', 'cotton', 'silk', 'synthetic', 'linen', 'light', 'bamboo', 'modal'],
}

LEGWEAR_TYPES = {
    'stockings': {'seasons': ['winter', 'fall', 'spring']},
    'tights': {'seasons': ['winter', 'fall']},
    'leggings': {'seasons': ['winter', 'fall', 'spring']},
}

class OutfitRequest(BaseModel):
    profile_name: str
    user_profile: Dict
    event_context: Dict
    material_preferences: Optional[List[str]] = None
    texture_preferences: Optional[List[str]] = None
    style_preferences: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "OutfitRequest":
        return cls(**data)

class SimpleOutfitRequest(BaseModel):
    """Simple outfit request for individual item generation."""
    user_profile: UserProfile
    event_context: EventContext

class OutfitItem(BaseModel):
    """Individual clothing item."""
    type: str
    color: str
    material: str
    fit: str
    style: str

class ShoeDetails(BaseModel):
    """Shoe-specific details."""
    type: str
    heel_height: str
    closure: str
    toe: str
    style: str
    material: str

class OutfitResponse(BaseModel):
    """Complete outfit response."""
    style_preferences: List[str]
    color_preferences: List[str]
    materials: List[str]
    suitability: str
    occasion: str
    season: str
    formality_level: int
    comfort_level: int
    top: OutfitItem
    bottom: OutfitItem
    shoes: ShoeDetails

class CompleteOutfitResponse(BaseModel):
    """Wrapper for outfit response."""
    outfit: OutfitResponse

class SingleItemResponse(BaseModel):
    """Response for single item generation."""
    pass

class TopResponse(SingleItemResponse):
    top: OutfitItem

class BottomResponse(SingleItemResponse):
    bottom: OutfitItem

class ShoesResponse(SingleItemResponse):
    shoes: ShoeDetails

class HauteCoutureOutfitResponse(BaseModel):
    design: HauteCoutureDesign
    materials: List[MaterialDetail]
    textures: List[TextureDetail]
    combinations: List[FabricCombination]
    timeline: Dict
    cost_breakdown: Dict

# Helper functions for outfit generation
def get_style_context(event_context: EventContext) -> str:
    """Determines style based on formality level."""
    if event_context.formality_level and event_context.formality_level >= 4:
        return 'formal'
    return 'casual'

def validate_material_for_season(material: str, season: str) -> bool:
    """Checks if material is appropriate for season."""
    if not season:
        return True
    return material in MATERIAL_COMBINATIONS.get(season, [])

def get_material_context(event_context: EventContext) -> List[str]:
    """Gets appropriate materials based on event context."""
    season = event_context.season or 'summer'
    return MATERIAL_COMBINATIONS.get(season, ['cotton', 'polyester'])

def get_appropriate_material(item_type: str, available_materials: List[str], season: str) -> str:
    """Selects appropriate material with seasonal validation."""
    for material in available_materials:
        if validate_material_for_season(material, season):
            return material
    return available_materials[0] if available_materials else 'cotton'

def get_appropriate_shoe_type(event_context: EventContext, user_profile: UserProfile) -> ShoeDetails:
    """Determines appropriate shoe type based on context."""
    formality = event_context.formality_level or 2
    season = event_context.season or 'summer'
    
    # Handle special requirements
    special_requirement = user_profile.model_dump().get('special_requirement')
    if special_requirement == 'pregnant':
        heel_height = 'flat'
    elif formality >= 4:
        heel_height = 'high'
    elif formality >= 3:
        heel_height = 'medium'
    else:
        heel_height = 'low'
    
    # Select shoe type based on formality and season
    if formality >= 4:
        shoe_type = 'heels'
        closure = 'slip-on'
    elif formality >= 3:
        shoe_type = 'flats'
        closure = 'slip-on'
    else:
        shoe_type = 'sneakers'
        closure = 'lace-up'
    
    return ShoeDetails(
        type=shoe_type,
        heel_height=heel_height,
        closure=closure,
        toe='closed',
        style=get_style_context(event_context),
        material='leather'
    )

def generate_outfit_item(item_type: str, request: SimpleOutfitRequest, available_materials: List[str]) -> OutfitItem:
    """Generates single outfit item with material restrictions."""
    season = request.event_context.season or 'summer'
    style = get_style_context(request.event_context)
    material = get_appropriate_material(item_type, available_materials, season)
    
    # Select appropriate colors
    color_prefs = request.user_profile.color_preferences or ['black', 'blue', 'gray']
    color = random.choice(color_prefs)
    
    # Select appropriate fit
    fit_prefs = request.user_profile.fit_preferences or ['regular']
    fit = random.choice(fit_prefs)
    
    # Select appropriate type based on item and context
    if item_type == 'top':
        if style == 'formal':
            top_type = random.choice(['blouse', 'shirt', 'sweater'])
        else:
            top_type = random.choice(['t-shirt', 'sweater', 'tank-top'])
    elif item_type == 'bottom':
        if style == 'formal':
            top_type = random.choice(['trousers', 'skirt'])
        else:
            top_type = random.choice(['jeans', 'pants', 'shorts'])
    else:
        top_type = item_type
    
    return OutfitItem(
        type=top_type,
        color=color,
        material=material,
        fit=fit,
        style=style
    )

@app.post("/api/generate/outfit", response_model=HauteCoutureOutfitResponse)
async def generate_outfit(request: OutfitRequest):
    try:
        # Get the requested profile
        profile = get_profile(request.profile_name)
        
        # Validate and process materials
        materials = []
        for material_name in (request.material_preferences or profile.recommended_materials):
            try:
                material_detail = material_specs.get_material_detail(material_name)
                # Convert properties to string if needed
                if isinstance(material_detail.properties, list):
                    material_detail.properties = ', '.join(material_detail.properties)
                materials.append(material_detail)
            except ValueError as e:
                logger.warning(f"Invalid material requested: {material_name}")
                continue

        # Process textures
        textures = []
        if request.texture_preferences:
            for texture_name in request.texture_preferences:
                try:
                    texture_detail = material_specs.get_texture_detail(texture_name)
                    textures.append(texture_detail)
                except ValueError as e:
                    logger.warning(f"Invalid texture requested: {texture_name}")
                    continue

        # Create fabric combinations
        combinations = []
        if len(materials) >= 2:
            for i in range(len(materials) - 1):
                combination = FabricCombination(
                    primary_material=materials[i].type,
                    secondary_material=materials[i + 1].type,
                    recommended_use=f"Combination of {materials[i].type} and {materials[i + 1].type}",
                    construction_notes=f"Special handling required for {materials[i].type} and {materials[i + 1].type} combination",
                    care_instructions=f"Follow care instructions for both {materials[i].type} and {materials[i + 1].type}"
                )
                combinations.append(combination)

        # Create complete design
        design = HauteCoutureDesign(
            profile=profile,
            materials=materials,
            textures=textures,
            combinations=combinations,
            measurements=request.user_profile.get("measurements", {}),
            timeline=profile.timeline,
            cost_breakdown={
                "materials": "30%",
                "labor": "45%",
                "fittings": "15%",
                "finishing": "10%"
            }
        )

        return HauteCoutureOutfitResponse(
            design=design,
            materials=materials,
            textures=textures,
            combinations=combinations,
            timeline=profile.timeline,
            cost_breakdown=design.cost_breakdown
        )

    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating outfit: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/generate/top", response_model=TopResponse)
async def generate_top(request: SimpleOutfitRequest):
    """Generate top only."""
    try:
        available_materials = get_material_context(request.event_context)
        top = generate_outfit_item('top', request, available_materials)
        return TopResponse(top=top)
    except Exception as e:
        logger.error(f"Error generating top: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/generate/bottom", response_model=BottomResponse)
async def generate_bottom(request: SimpleOutfitRequest):
    """Generate bottom only."""
    try:
        available_materials = get_material_context(request.event_context)
        bottom = generate_outfit_item('bottom', request, available_materials)
        return BottomResponse(bottom=bottom)
    except Exception as e:
        logger.error(f"Error generating bottom: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/generate/shoes", response_model=ShoesResponse)
async def generate_shoes(request: SimpleOutfitRequest):
    """Generate shoes only."""
    try:
        shoes = get_appropriate_shoe_type(request.event_context, request.user_profile)
        return ShoesResponse(shoes=shoes)
    except Exception as e:
        logger.error(f"Error generating shoes: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/generate/complete-outfit", response_model=CompleteOutfitResponse)
async def generate_complete_outfit(request: SimpleOutfitRequest):
    """Generate complete outfit."""
    try:
        available_materials = get_material_context(request.event_context)
        
        # Generate individual items
        top = generate_outfit_item('top', request, available_materials)
        bottom = generate_outfit_item('bottom', request, available_materials)
        shoes = get_appropriate_shoe_type(request.event_context, request.user_profile)
        
        # Create complete outfit response
        outfit = OutfitResponse(
            style_preferences=request.user_profile.style_preferences or ['casual'],
            color_preferences=request.user_profile.color_preferences or ['black', 'blue'],
            materials=available_materials,
            suitability='appropriate',
            occasion=request.event_context.event_type or 'casual',
            season=request.event_context.season or 'summer',
            formality_level=request.event_context.formality_level or 2,
            comfort_level=request.user_profile.comfort_level or 5,
            top=top,
            bottom=bottom,
            shoes=shoes
        )
        
        return CompleteOutfitResponse(outfit=outfit)
    except Exception as e:
        logger.error(f"Error generating complete outfit: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/profiles")
async def get_profiles():
    """Get list of available haute couture profiles."""
    try:
        profiles = {}
        for profile_name in list_profiles():
            profiles[profile_name] = get_profile_details(profile_name)
        return JSONResponse(content=profiles)
    except Exception as e:
        logger.error(f"Error getting profiles: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/profile/{profile_name}")
async def get_profile_info(profile_name: str):
    """Get detailed information about a specific profile."""
    try:
        return JSONResponse(content=get_profile_details(profile_name))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting profile {profile_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/materials")
async def get_materials():
    """Get list of available materials with their properties."""
    try:
        materials = {}
        for material_name in material_specs.material_properties.keys():
            materials[material_name] = material_specs.get_material_detail(material_name).dict()
        return JSONResponse(content=materials)
    except Exception as e:
        logger.error(f"Error getting materials: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/textures")
async def get_textures():
    """Get list of available textures with their properties."""
    try:
        textures = {}
        for texture_name in material_specs.texture_properties.keys():
            textures[texture_name] = material_specs.get_texture_detail(texture_name).dict()
        return JSONResponse(content=textures)
    except Exception as e:
        logger.error(f"Error getting textures: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all requests."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Request {request.method} {request.url.path} completed in {process_time:.2f}s")
    return response
