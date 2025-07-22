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

app = FastAPI()

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

# Initialize material specifications
material_specs = MaterialSpecifications()

# Material and legwear constants for testing
MATERIAL_COMBINATIONS = {
    "spring": ["cotton", "linen", "silk", "lightweight wool"],
    "summer": ["cotton", "linen", "silk", "bamboo", "modal"],
    "fall": ["wool", "cashmere", "cotton blends", "denim"],
    "winter": ["wool", "cashmere", "down", "fleece", "thermal"]
}

LEGWEAR_TYPES = {
    "pants": {"seasons": ["spring", "summer", "fall", "winter"]},
    "jeans": {"seasons": ["spring", "fall", "winter"]},
    "shorts": {"seasons": ["spring", "summer"]},
    "skirt": {"seasons": ["spring", "summer", "fall"]},
    "dress": {"seasons": ["spring", "summer", "fall"]},
    "leggings": {"seasons": ["fall", "winter", "spring"]},
    "trousers": {"seasons": ["spring", "fall", "winter"]}
}

class UserProfile(BaseModel):
    """User profile with measurements and preferences."""
    height: Optional[float] = None
    weight: Optional[float] = None
    bust: Optional[float] = None
    waist: Optional[float] = None
    hips: Optional[float] = None
    inseam: Optional[float] = None
    shoe_size: Optional[float] = None
    comfort_level: Optional[int] = Field(ge=1, le=5, default=3)
    style_preferences: List[str] = []
    color_preferences: List[str] = []
    fit_preferences: List[str] = []
    user_id: Optional[str] = None

class EventContext(BaseModel):
    """Context information for outfit generation."""
    event_type: str
    formality_level: int = Field(ge=1, le=5, default=3)
    weather_conditions: List[str] = []
    time_of_day: Optional[str] = None
    season: Optional[str] = None
    location: Optional[str] = None
    duration: Optional[int] = None  # Duration in minutes
    activity_level: Optional[int] = Field(ge=1, le=5, default=3)

class OutfitRequest(BaseModel):
    profile_name: str
    user_profile: Dict
    event_context: Dict
    material_preferences: Optional[List[str]] = None
    texture_preferences: Optional[List[str]] = None
    style_preferences: Optional[List[str]] = None

class OutfitResponse(BaseModel):
    design: HauteCoutureDesign
    materials: List[MaterialDetail]
    textures: List[TextureDetail]
    combinations: List[FabricCombination]
    timeline: Dict
    cost_breakdown: Dict

@app.post("/api/generate/outfit", response_model=OutfitResponse)
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

        return OutfitResponse(
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

# Measurement validation endpoints
@app.post("/api/measurements/validate")
async def validate_measurements(profile: UserProfile):
    """Validate user measurements."""
    try:
        # Basic validation logic
        errors = []
        
        if profile.height and (profile.height < 100 or profile.height > 250):
            errors.append("Height must be between 100 and 250 cm")
        
        if profile.weight and (profile.weight < 20 or profile.weight > 300):
            errors.append("Weight must be between 20 and 300 kg")
            
        if profile.comfort_level and (profile.comfort_level < 1 or profile.comfort_level > 5):
            errors.append("Comfort level must be between 1 and 5")
        
        return JSONResponse({
            "valid": len(errors) == 0,
            "errors": errors,
            "measurements": profile.model_dump()
        })
    except Exception as e:
        logger.error(f"Error validating measurements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/measurements/estimate")
async def estimate_measurements(profile: UserProfile):
    """Estimate missing measurements based on available data."""
    try:
        estimator = MeasurementEstimator()
        measurements = profile.model_dump()
        
        # Basic estimation logic
        if profile.height and profile.weight:
            if not profile.bust:
                measurements["bust"] = profile.height * 0.5  # Simple estimation
            if not profile.waist:
                measurements["waist"] = profile.height * 0.4
            if not profile.hips:
                measurements["hips"] = profile.height * 0.53
            if not profile.inseam:
                measurements["inseam"] = profile.height * 0.45
        
        # Determine body type for estimated measurements
        if all([measurements.get("bust"), measurements.get("waist"), measurements.get("hips")]):
            bust_hip_diff = abs(measurements["bust"] - measurements["hips"])
            waist_diff = min(measurements["bust"] - measurements["waist"], measurements["hips"] - measurements["waist"])
            
            if bust_hip_diff <= 2 and waist_diff >= 8:
                body_type = "hourglass"
            elif measurements["bust"] > measurements["hips"] + 2:
                body_type = "apple"
            elif measurements["hips"] > measurements["bust"] + 2:
                body_type = "pear"
            else:
                body_type = "rectangle"
        else:
            body_type = "unknown"
        
        return JSONResponse({
            "measurements": measurements,
            "body_type": body_type
        })
    except Exception as e:
        logger.error(f"Error estimating measurements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/measurements/guide")
async def get_measurement_guide():
    """Get measurement guide and instructions."""
    guide = {
        "guide": {
            "instructions": {
                "height": "Measure against a wall without shoes",
                "weight": "Use a calibrated scale, preferably in the morning",
                "bust": "Measure around the fullest part of the bust",
                "waist": "Measure around the narrowest part of the waist",
                "hips": "Measure around the fullest part of the hips",
                "inseam": "Measure from crotch to ankle bone"
            },
            "tips": [
                "Take measurements over light clothing or undergarments",
                "Ensure measuring tape is parallel to the ground",
                "Don't pull the measuring tape too tight"
            ]
        },
        "default_measurements": {
            "height": 170,
            "weight": 65,
            "bust": 88,
            "waist": 68,
            "hips": 92,
            "inseam": 76
        },
        "valid_ranges": {
            "height": {"min": 100, "max": 250},
            "weight": {"min": 20, "max": 300},
            "bust": {"min": 60, "max": 150},
            "waist": {"min": 50, "max": 120},
            "hips": {"min": 60, "max": 150},
            "inseam": {"min": 50, "max": 120}
        }
    }
    return JSONResponse(guide)

@app.post("/api/measurements/body-type")
async def determine_body_type(profile: UserProfile):
    """Determine body type based on measurements."""
    try:
        if not all([profile.bust, profile.waist, profile.hips]):
            return JSONResponse({
                "error": "Bust, waist, and hip measurements required",
                "body_type": None,
                "characteristics": {},
                "measurements": profile.model_dump()
            })
        
        # Simple body type determination logic
        bust_hip_diff = abs(profile.bust - profile.hips)
        waist_diff = min(profile.bust - profile.waist, profile.hips - profile.waist)
        
        if bust_hip_diff <= 2 and waist_diff >= 8:
            body_type = "hourglass"
            characteristics = {
                "description": "Balanced bust and hips with defined waist",
                "strengths": ["Well-defined waist", "Balanced proportions"],
                "style_tips": ["Emphasize waist", "Balanced silhouettes"]
            }
        elif profile.bust > profile.hips + 2:
            body_type = "apple"
            characteristics = {
                "description": "Fuller bust and narrower hips",
                "strengths": ["Great legs", "Attractive bust line"],
                "style_tips": ["Emphasize legs", "Draw attention to shoulders"]
            }
        elif profile.hips > profile.bust + 2:
            body_type = "pear"
            characteristics = {
                "description": "Fuller hips and narrower bust",
                "strengths": ["Defined waist", "Balanced upper body"],
                "style_tips": ["Emphasize upper body", "A-line silhouettes"]
            }
        else:
            body_type = "rectangle"
            characteristics = {
                "description": "Similar bust, waist, and hip measurements",
                "strengths": ["Long, lean lines", "Versatile body type"],
                "style_tips": ["Create curves", "Add definition to waist"]
            }
        
        return JSONResponse({
            "body_type": body_type,
            "characteristics": characteristics,
            "measurements": profile.model_dump(),
            "recommendations": f"Style recommendations for {body_type} body type"
        })
    except Exception as e:
        logger.error(f"Error determining body type: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Outfit generation endpoints
@app.post("/api/generate/top")
async def generate_top(request: dict):
    """Generate top recommendation."""
    try:
        return JSONResponse({
            "top": {
                "type": "shirt",
                "color": "white",
                "material": "cotton",
                "fit": "regular",
                "style": "classic"
            },
            "reasoning": "Versatile and suitable for most occasions"
        })
    except Exception as e:
        logger.error(f"Error generating top: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/bottom")
async def generate_bottom(request: dict):
    """Generate bottom recommendation."""
    try:
        return JSONResponse({
            "bottom": {
                "type": "jeans",
                "color": "dark blue",
                "material": "denim",
                "fit": "straight",
                "style": "classic"
            },
            "reasoning": "Classic and versatile choice"
        })
    except Exception as e:
        logger.error(f"Error generating bottom: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/shoes")
async def generate_shoes(request: dict):
    """Generate shoes recommendation."""
    try:
        return JSONResponse({
            "shoes": {
                "type": "sneakers",
                "heel_height": "flat",
                "closure": "lace-up",
                "toe": "round",
                "style": "casual",
                "material": "leather"
            },
            "reasoning": "Comfortable and versatile"
        })
    except Exception as e:
        logger.error(f"Error generating shoes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/complete-outfit")
async def generate_complete_outfit(request: dict):
    """Generate complete outfit recommendation."""
    try:
        # Check for special requirements
        user_profile = request.get("user_profile", {})
        special_requirement = user_profile.get("special_requirement")
        
        # Adjust heel height based on special requirements
        heel_height = "flat" if special_requirement == "PREGNANT" else "low"
        
        outfit = {
            "outfit": {
                "style_preferences": ["casual", "classic"],
                "color_preferences": ["white", "navy", "brown"],
                "materials": ["cotton", "denim", "leather"],
                "suitability": "high",
                "occasion": "casual gathering",
                "season": "summer",
                "formality_level": 3,
                "comfort_level": 4,
                "top": {
                    "item": "Button-down shirt",
                    "color": "white",
                    "material": "cotton"
                },
                "bottom": {
                    "item": "Chinos",
                    "color": "navy",
                    "material": "cotton"
                },
                "shoes": {
                    "item": "Loafers",
                    "color": "brown",
                    "material": "leather",
                    "heel_height": heel_height
                },
                "accessories": [
                    {"item": "belt", "color": "brown", "material": "leather"}
                ]
            },
            "outfit_id": f"outfit_{int(time.time())}",
            "style_score": 85
        }
        
        return JSONResponse(outfit)
    except Exception as e:
        logger.error(f"Error generating complete outfit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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