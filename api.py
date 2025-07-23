from fastapi import FastAPI, HTTPException, Request, Response, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, ValidationError, field_validator
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
from datetime import datetime, timedelta
import hashlib
import hmac
import secrets
import os
from collections import defaultdict
from functools import lru_cache
import asyncio

# Test mode configuration
TEST_MODE = os.getenv("DRESSUP_TEST_MODE", "false").lower() == "true"

# Simple in-memory cache for outfit generation
outfit_cache = {}
CACHE_TTL = 3600  # 1 hour cache TTL

# Performance monitoring
request_metrics = defaultdict(list)

def record_request_time(endpoint: str, duration: float):
    """Record request processing time for monitoring."""
    request_metrics[endpoint].append({
        "duration": duration,
        "timestamp": time.time()
    })
    
    # Keep only last 100 entries per endpoint
    if len(request_metrics[endpoint]) > 100:
        request_metrics[endpoint] = request_metrics[endpoint][-100:]

app = FastAPI(
    title="DressUp AI API",
    description="AI-powered fashion outfit generation system",
    version="1.0.0"
)

# Security configuration
security = HTTPBearer(auto_error=False)

# Simple in-memory storage for demo (use proper database in production)
API_KEYS = {
    "demo_key_123": {"user_id": "demo_user", "permissions": ["read", "write"]},
    "admin_key_456": {"user_id": "admin_user", "permissions": ["read", "write", "admin"]}
}

# Rate limiting storage
rate_limit_storage = defaultdict(list)
RATE_LIMIT_REQUESTS = 100  # requests per window
RATE_LIMIT_WINDOW = 3600  # window in seconds (1 hour)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict:
    """Get current user info from API key (optional authentication)."""
    if TEST_MODE or credentials is None:
        return {"user_id": "anonymous", "permissions": ["read"]}
    
    token = credentials.credentials
    if token in API_KEYS:
        return API_KEYS[token]
    
    # For now, allow access but log the invalid key
    logger.warning(f"Invalid API key attempted: {token[:10]}...")
    return {"user_id": "anonymous", "permissions": ["read"]}

def check_rate_limit(request: Request) -> bool:
    """Check if request is within rate limits."""
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old entries
    rate_limit_storage[client_ip] = [
        timestamp for timestamp in rate_limit_storage[client_ip]
        if current_time - timestamp < RATE_LIMIT_WINDOW
    ]
    
    # Check if limit exceeded
    if len(rate_limit_storage[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Add current request
    rate_limit_storage[client_ip].append(current_time)
    return True

def get_cache_key(request_data: dict) -> str:
    """Generate cache key from request data."""
    # Create a deterministic cache key from the request
    import hashlib
    import json
    serialized = json.dumps(request_data, sort_keys=True)
    return hashlib.md5(serialized.encode()).hexdigest()

def get_cached_outfit(cache_key: str) -> Optional[dict]:
    """Get cached outfit if still valid."""
    if cache_key in outfit_cache:
        cached_data, timestamp = outfit_cache[cache_key]
        if time.time() - timestamp < CACHE_TTL:
            return cached_data
        else:
            # Remove expired cache entry
            del outfit_cache[cache_key]
    return None

def cache_outfit(cache_key: str, outfit_data: dict):
    """Cache outfit data."""
    outfit_cache[cache_key] = (outfit_data, time.time())

@lru_cache(maxsize=128)
def get_cached_material_detail(material_name: str):
    """Cache material details lookup."""
    try:
        return material_specs.get_material_detail(material_name)
    except ValueError:
        return None

# Advanced AI features for outfit generation
def analyze_color_harmony(color_preferences: List[str]) -> Dict:
    """Analyze color harmony and suggest complementary colors."""
    color_harmony_map = {
        "red": {"complementary": ["green"], "analogous": ["orange", "pink"], "triadic": ["blue", "yellow"]},
        "blue": {"complementary": ["orange"], "analogous": ["purple", "teal"], "triadic": ["red", "yellow"]},
        "green": {"complementary": ["red"], "analogous": ["blue", "yellow"], "triadic": ["purple", "orange"]},
        "yellow": {"complementary": ["purple"], "analogous": ["orange", "green"], "triadic": ["red", "blue"]},
        "purple": {"complementary": ["yellow"], "analogous": ["blue", "red"], "triadic": ["green", "orange"]},
        "orange": {"complementary": ["blue"], "analogous": ["red", "yellow"], "triadic": ["green", "purple"]},
        "black": {"complementary": ["white"], "analogous": ["gray"], "triadic": ["white", "gray"]},
        "white": {"complementary": ["black"], "analogous": ["gray"], "triadic": ["black", "gray"]},
        "navy": {"complementary": ["cream"], "analogous": ["blue", "teal"], "triadic": ["burgundy", "gold"]},
        "brown": {"complementary": ["blue"], "analogous": ["orange", "red"], "triadic": ["green", "purple"]}
    }
    
    analysis = {
        "primary_colors": color_preferences[:3],
        "suggested_combinations": [],
        "harmony_score": 0.8  # Default harmony score
    }
    
    for color in color_preferences[:2]:  # Analyze top 2 colors
        if color.lower() in color_harmony_map:
            harmony_data = color_harmony_map[color.lower()]
            analysis["suggested_combinations"].extend(harmony_data.get("complementary", []))
    
    return analysis

def calculate_style_compatibility(style_preferences: List[str], event_type: str) -> Dict:
    """Calculate style compatibility for the given event."""
    
    style_event_map = {
        "casual": {"compatible": ["casual", "relaxed", "comfortable", "everyday"], "score_multiplier": 1.0},
        "business": {"compatible": ["formal", "professional", "classic", "structured"], "score_multiplier": 0.9},
        "formal": {"compatible": ["formal", "elegant", "sophisticated", "classic"], "score_multiplier": 0.8},
        "party": {"compatible": ["trendy", "bold", "fashionable", "statement"], "score_multiplier": 0.9},
        "athletic": {"compatible": ["sporty", "comfortable", "functional", "active"], "score_multiplier": 1.0},
        "date": {"compatible": ["romantic", "elegant", "attractive", "stylish"], "score_multiplier": 0.9}
    }
    
    event_lower = event_type.lower()
    compatibility = style_event_map.get(event_lower, style_event_map["casual"])
    
    # Calculate compatibility score
    score = 0.5  # Base score
    for style in style_preferences:
        if style.lower() in compatibility["compatible"]:
            score += 0.2
    
    score = min(score * compatibility["score_multiplier"], 1.0)
    
    return {
        "compatibility_score": score,
        "recommended_styles": compatibility["compatible"][:3],
        "event_appropriateness": "high" if score > 0.7 else "medium" if score > 0.5 else "low"
    }

def generate_pattern_recommendations(style_preferences: List[str], season: str) -> Dict:
    """Generate pattern recommendations based on style and season."""
    
    seasonal_patterns = {
        "spring": ["floral", "stripes", "polka dots", "geometric"],
        "summer": ["tropical", "nautical", "abstract", "bright geometrics"],
        "fall": ["plaid", "houndstooth", "paisley", "earth tones"],
        "winter": ["solid colors", "subtle textures", "minimal patterns", "classic stripes"]
    }
    
    style_patterns = {
        "classic": ["stripes", "solid colors", "subtle textures"],
        "trendy": ["geometric", "abstract", "bold patterns"],
        "romantic": ["floral", "lace textures", "soft patterns"],
        "edgy": ["animal print", "geometric", "bold contrasts"],
        "minimalist": ["solid colors", "subtle textures", "monochrome"]
    }
    
    recommendations = []
    
    # Season-based recommendations
    season_lower = season.lower() if season else "spring"
    if season_lower in seasonal_patterns:
        recommendations.extend(seasonal_patterns[season_lower][:2])
    
    # Style-based recommendations
    for style in style_preferences[:2]:
        style_lower = style.lower()
        if style_lower in style_patterns:
            recommendations.extend(style_patterns[style_lower][:2])
    
    # Remove duplicates and limit
    recommendations = list(dict.fromkeys(recommendations))[:4]
    
    return {
        "recommended_patterns": recommendations,
        "pattern_confidence": 0.8,
        "seasonal_appropriateness": "high"
    }

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    if not check_rate_limit(request):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again later."}
        )
    return await call_next(request)

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

# CORS configuration - more restrictive for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000"],  # Add specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-Total-Count"]
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
    height: Optional[float] = Field(None, ge=100, le=250, description="Height in cm")
    weight: Optional[float] = Field(None, ge=20, le=300, description="Weight in kg")
    bust: Optional[float] = Field(None, ge=60, le=150, description="Bust measurement in cm")
    waist: Optional[float] = Field(None, ge=50, le=120, description="Waist measurement in cm")
    hips: Optional[float] = Field(None, ge=60, le=150, description="Hip measurement in cm")
    inseam: Optional[float] = Field(None, ge=50, le=120, description="Inseam measurement in cm")
    shoe_size: Optional[float] = Field(None, ge=30, le=50, description="Shoe size")
    comfort_level: Optional[int] = Field(3, ge=1, le=5, description="Comfort level preference")
    style_preferences: List[str] = Field(default=[], max_length=10, description="Style preferences")
    color_preferences: List[str] = Field(default=[], max_length=15, description="Color preferences")
    fit_preferences: List[str] = Field(default=[], max_length=10, description="Fit preferences")
    user_id: Optional[str] = Field(None, max_length=50, description="User identifier")
    
    @field_validator('style_preferences', 'color_preferences', 'fit_preferences')
    def validate_preferences(cls, v):
        if isinstance(v, list):
            # Sanitize input - remove any potential script tags or harmful content
            sanitized = []
            for item in v:
                if isinstance(item, str) and len(item.strip()) > 0:
                    # Remove potential harmful characters
                    clean_item = item.strip()[:50]  # Limit length
                    if not any(char in clean_item for char in ['<', '>', '{', '}', ';']):
                        sanitized.append(clean_item)
            return sanitized
        return []

class EventContext(BaseModel):
    """Context information for outfit generation."""
    event_type: str = Field(..., max_length=100, description="Type of event")
    formality_level: int = Field(3, ge=1, le=5, description="Formality level")
    weather_conditions: List[str] = Field(default=[], max_length=5, description="Weather conditions")
    time_of_day: Optional[str] = Field(None, max_length=20, description="Time of day")
    season: Optional[str] = Field(None, max_length=20, description="Season")
    location: Optional[str] = Field(None, max_length=100, description="Event location")
    duration: Optional[int] = Field(None, ge=1, le=1440, description="Duration in minutes")
    activity_level: Optional[int] = Field(3, ge=1, le=5, description="Activity level")
    
    @field_validator('event_type', 'time_of_day', 'season', 'location')
    def validate_text_fields(cls, v):
        if v is not None:
            # Sanitize text input
            clean_text = str(v).strip()[:100]
            if any(char in clean_text for char in ['<', '>', '{', '}', ';', '"', "'"]):
                raise ValueError("Invalid characters in text field")
            return clean_text
        return v

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

# Public endpoints (no authentication required)
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.get("/api/metrics")
async def get_metrics():
    """Get API performance metrics."""
    metrics = {}
    for endpoint, requests in request_metrics.items():
        if requests:
            durations = [r["duration"] for r in requests]
            metrics[endpoint] = {
                "total_requests": len(requests),
                "avg_response_time": sum(durations) / len(durations),
                "min_response_time": min(durations),
                "max_response_time": max(durations)
            }
    
    return JSONResponse({
        "metrics": metrics,
        "cache_stats": {
            "total_cached_items": len(outfit_cache),
            "cache_hit_ratio": "N/A"  # Would track this in production
        },
        "rate_limit_stats": {
            "active_clients": len(rate_limit_storage)
        }
    })

@app.get("/api/measurements/guide")
async def get_measurement_guide():
    """Get measurement guide and instructions (public endpoint)."""
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

# Authenticated endpoints
@app.post("/api/measurements/validate")
async def validate_measurements(profile: UserProfile, user_info: Dict = Depends(get_current_user)):
    """Validate user measurements (requires authentication)."""
    try:
        # Basic validation logic
        errors = []
        
        if profile.height and (profile.height < 100 or profile.height > 250):
            errors.append("Height must be between 100 and 250 cm")
        
        if profile.weight and (profile.weight < 20 or profile.weight > 300):
            errors.append("Weight must be between 20 and 300 kg")
            
        if profile.comfort_level and (profile.comfort_level < 1 or profile.comfort_level > 5):
            errors.append("Comfort level must be between 1 and 5")
        
        logger.info(f"User {user_info['user_id']} validated measurements")
        
        return JSONResponse({
            "valid": len(errors) == 0,
            "errors": errors,
            "measurements": profile.model_dump()
        })
    except Exception as e:
        logger.error(f"Error validating measurements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/measurements/estimate")
async def estimate_measurements(profile: UserProfile, user_info: Dict = Depends(get_current_user)):
    """Estimate missing measurements based on available data (requires authentication)."""
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
        
        logger.info(f"User {user_info['user_id']} estimated measurements")
        
        return JSONResponse({
            "measurements": measurements,
            "body_type": body_type
        })
    except Exception as e:
        logger.error(f"Error estimating measurements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/measurements/body-type")
async def determine_body_type(profile: UserProfile, user_info: Dict = Depends(get_current_user)):
    """Determine body type based on measurements (requires authentication)."""
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
        
        logger.info(f"User {user_info['user_id']} determined body type: {body_type}")
        
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
        # Check cache first
        cache_key = get_cache_key(request)
        cached_outfit = get_cached_outfit(cache_key)
        if cached_outfit:
            logger.info(f"Returning cached outfit for key: {cache_key[:8]}...")
            return JSONResponse(cached_outfit)
        
        # Check for special requirements
        user_profile = request.get("user_profile", {})
        event_context = request.get("event_context", {})
        special_requirement = user_profile.get("special_requirement")
        
        # Simulate async processing delay for complex generation
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Advanced AI features
        color_analysis = analyze_color_harmony(user_profile.get("color_preferences", []))
        style_match = calculate_style_compatibility(
            user_profile.get("style_preferences", []), 
            event_context.get("event_type", "casual")
        )
        pattern_analysis = generate_pattern_recommendations(
            user_profile.get("style_preferences", []),
            event_context.get("season", "spring")
        )
        
        # Adjust heel height based on special requirements
        heel_height = "flat" if special_requirement == "PREGNANT" else "low"
        
        # Use AI analysis to enhance outfit
        primary_colors = color_analysis.get("primary_colors", ["white", "navy", "brown"])
        recommended_styles = style_match.get("recommended_styles", ["casual", "classic"])
        
        outfit = {
            "outfit": {
                "style_preferences": recommended_styles[:2],
                "color_preferences": primary_colors[:3],
                "materials": ["cotton", "denim", "leather"],
                "suitability": style_match.get("event_appropriateness", "high"),
                "occasion": event_context.get("event_type", "casual gathering"),
                "season": event_context.get("season", "summer"),
                "formality_level": event_context.get("formality_level", 3),
                "comfort_level": user_profile.get("comfort_level", 4),
                "top": {
                    "item": "Button-down shirt",
                    "color": primary_colors[0] if primary_colors else "white",
                    "material": "cotton",
                    "pattern": pattern_analysis.get("recommended_patterns", ["solid"])[0]
                },
                "bottom": {
                    "item": "Chinos",
                    "color": primary_colors[1] if len(primary_colors) > 1 else "navy",
                    "material": "cotton",
                    "pattern": "solid"
                },
                "shoes": {
                    "item": "Loafers",
                    "color": primary_colors[2] if len(primary_colors) > 2 else "brown",
                    "material": "leather",
                    "heel_height": heel_height
                },
                "accessories": [
                    {"item": "belt", "color": primary_colors[2] if len(primary_colors) > 2 else "brown", "material": "leather"}
                ]
            },
            "outfit_id": f"outfit_{int(time.time())}",
            "style_score": int(style_match.get("compatibility_score", 0.85) * 100),
            "ai_analysis": {
                "color_harmony": color_analysis,
                "style_compatibility": style_match,
                "pattern_recommendations": pattern_analysis
            }
        }
        
        # Cache the generated outfit
        cache_outfit(cache_key, outfit)
        logger.info(f"Cached new outfit for key: {cache_key[:8]}...")
        
        return JSONResponse(outfit)
    except Exception as e:
        logger.error(f"Error generating complete outfit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Advanced AI endpoints
@app.post("/api/ai/color-analysis")
async def analyze_colors(request: dict):
    """Analyze color combinations and provide recommendations."""
    try:
        colors = request.get("colors", [])
        style_context = request.get("style_context", "casual")
        
        if not colors:
            raise HTTPException(status_code=400, detail="Colors list cannot be empty")
        
        analysis = analyze_color_harmony(colors)
        
        return JSONResponse({
            "analysis": analysis,
            "recommendations": {
                "primary_palette": analysis["primary_colors"],
                "suggested_combinations": analysis["suggested_combinations"],
                "harmony_score": analysis["harmony_score"],
                "style_context": style_context
            },
            "tips": [
                "Use the 60-30-10 rule: 60% dominant color, 30% secondary, 10% accent",
                "Consider your skin tone when choosing colors",
                "Neutral colors can balance bold choices"
            ]
        })
    except Exception as e:
        logger.error(f"Error in color analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/style-match")
async def analyze_style_compatibility(request: dict):
    """Analyze style compatibility for events and occasions."""
    try:
        styles = request.get("style_preferences", [])
        event_type = request.get("event_type", "casual")
        
        compatibility = calculate_style_compatibility(styles, event_type)
        
        return JSONResponse({
            "compatibility": compatibility,
            "recommendations": {
                "suggested_adjustments": [],
                "alternative_styles": compatibility["recommended_styles"],
                "confidence_level": compatibility["compatibility_score"]
            }
        })
    except Exception as e:
        logger.error(f"Error in style compatibility analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/pattern-recommendations")
async def get_pattern_recommendations(request: dict):
    """Get pattern recommendations based on style and season."""
    try:
        styles = request.get("style_preferences", [])
        season = request.get("season", "spring")
        
        recommendations = generate_pattern_recommendations(styles, season)
        
        return JSONResponse({
            "recommendations": recommendations,
            "styling_tips": [
                "Mix patterns of different scales for visual interest",
                "Keep one pattern dominant and others subtle",
                "Solid colors can break up busy patterns"
            ]
        })
    except Exception as e:
        logger.error(f"Error generating pattern recommendations: {str(e)}")
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
    """Middleware to log all requests and record performance metrics."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Record metrics
    endpoint = f"{request.method} {request.url.path}"
    record_request_time(endpoint, process_time)
    
    logger.info(f"Request {request.method} {request.url.path} completed in {process_time:.2f}s")
    return response