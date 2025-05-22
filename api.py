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