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
import logging
import time
from datetime import datetime
from material_specs import MaterialSpecifications

app = FastAPI()

# Configure logging with more detailed format
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

# Custom exceptions
class OutfitGenerationError(Exception):
    """Raised when there's an error generating an outfit."""
    pass

class MaterialSelectionError(Exception):
    """Raised when there's an error selecting materials."""
    pass

class MeasurementValidationError(Exception):
    """Raised when there's an error validating measurements."""
    pass

class UserProfile(BaseModel):
    height: float
    weight: float
    bust: float
    underbust: Optional[float] = None
    cup_size: Optional[str] = None
    waist: float
    hips: float
    shoulder_width: Optional[float] = None
    arm_length: Optional[float] = None
    inseam: float
    shoe_size: float
    age: Optional[int] = None
    body_type: Optional[str] = None
    special_requirement: Optional[str] = None
    measurement_system: str = "metric"
    comfort_level: int
    style_preferences: List[str]
    color_preferences: List[str]
    fit_preferences: List[str]

    @classmethod
    def from_dict(cls, data: Dict):
        """Create a UserProfile from a dictionary."""
        # Estimate missing measurements if needed
        if not all(key in data for key in ['height', 'weight', 'bust', 'waist', 'hips']):
            estimator = MeasurementEstimator()
            estimated = estimator.estimate_missing_measurements(data)
            data.update(estimated)
        
        # Validate measurements
        validator = MeasurementValidation()
        is_valid, errors = validator.validate_measurements(data)
        if not is_valid:
            raise ValueError(f"Invalid measurements: {errors}")
        
        return cls(**data)

class EventContext(BaseModel):
    event_type: str
    formality_level: int
    weather_conditions: List[str]
    time_of_day: str
    season: str
    location: str
    duration: int
    activity_level: int

    @classmethod
    def from_dict(cls, data: Dict):
        """Create an EventContext from a dictionary."""
        return cls(**data)

class OutfitRequest(BaseModel):
    user_profile: UserProfile
    event_context: EventContext

    @classmethod
    def from_dict(cls, data: Dict) -> 'OutfitRequest':
        """Create an OutfitRequest from a dictionary."""
        return cls(
            user_profile=UserProfile(**data['user_profile']),
            event_context=EventContext(**data['event_context'])
        )

class OutfitItem(BaseModel):
    type: str
    color: str
    material: str
    fit: str
    style: str

class LegwearItem(BaseModel):
    type: str  # stockings, leggings, fishnets, tights, shorts, none
    color: str
    material: str
    opacity: Optional[str] = None  # sheer, opaque, semi-opaque
    pattern: Optional[str] = None  # solid, lace, mesh, etc.

class DressItem(BaseModel):
    type: str  # dress
    color: str
    material: str
    fit: str
    style: str
    length: str  # mini, midi, maxi, etc.
    neckline: Optional[str] = None  # v-neck, round, square, etc.
    sleeve_type: Optional[str] = None  # sleeveless, short-sleeve, long-sleeve, etc.

class ShoeDetails(BaseModel):
    type: str
    heel_height: str
    closure: str
    toe: str
    style: str
    material: Optional[str] = None

class OutfitResponse(BaseModel):
    style_preferences: List[str]
    color_preferences: List[str]
    materials: List[str]
    suitability: str = 'appropriate'
    occasion: str
    season: str
    formality_level: int
    comfort_level: int
    top: Optional[OutfitItem] = None
    bottom: Optional[OutfitItem] = None
    dress: Optional[DressItem] = None
    legwear: Optional[LegwearItem] = None
    shoes: ShoeDetails

class CompleteOutfitResponse(BaseModel):
    outfit: OutfitResponse

# Style inspiration for different contexts
STYLE_INSPIRATIONS = {
    'casual': {
        'tops': ['relaxed t-shirt', 'flowy blouse', 'soft sweater', 'casual tank', 'oversized shirt'],
        'bottoms': ['relaxed jeans', 'casual chinos', 'flowy shorts', 'comfortable skirt', 'soft leggings'],
        'shoes': ['comfortable sneakers', 'casual sandals', 'soft loafers', 'walking boots', 'easy flats']
    },
    'business': {
        'tops': ['button-down shirt', 'professional blouse', 'tailored blazer', 'business sweater', 'structured top'],
        'bottoms': ['dress pants', 'pencil skirt', 'tailored trousers', 'knee-length skirt', 'business slacks'],
        'shoes': ['business flats', 'low heels', 'oxford shoes', 'professional loafers', 'dress boots']
    },
    'formal': {
        'tops': ['elegant blouse', 'structured shirt', 'silk top', 'formal blouse', 'sophisticated top'],
        'bottoms': ['tailored pants', 'structured skirt', 'formal trousers', 'elegant skirt', 'sophisticated pants'],
        'shoes': ['elegant heels', 'formal pumps', 'sophisticated flats', 'dress shoes', 'formal sandals']
    }
}

# Shoe type definitions with detailed attributes
SHOE_TYPES = {
    'flats': {
        'types': ['ballet flats', 'loafers', 'mules', 'espadrilles', 'driving shoes'],
        'heel_height': ['flat'],
        'closure': ['slip-on', 'elastic', 'buckle'],
        'toe': ['closed', 'peep-toe'],
        'style': ['casual', 'business', 'semi-formal']
    },
    'sandals': {
        'types': ['strappy sandals', 'gladiator sandals', 'slide sandals', 'wedge sandals', 'platform sandals'],
        'heel_height': ['flat', 'low', 'medium', 'high'],
        'closure': ['strappy', 'slip-on', 'buckle'],
        'toe': ['open', 'peep-toe'],
        'style': ['casual', 'semi-formal', 'formal']
    },
    'heels': {
        'types': ['pumps', 'stilettos', 'block heels', 'kitten heels', 'platform heels'],
        'heel_height': ['low', 'medium', 'high'],
        'closure': ['slip-on', 'strappy', 'buckle'],
        'toe': ['closed', 'peep-toe', 'open'],
        'style': ['business', 'semi-formal', 'formal']
    },
    'wedges': {
        'types': ['wedge sandals', 'wedge espadrilles', 'wedge pumps', 'wedge boots'],
        'heel_height': ['low', 'medium', 'high'],
        'closure': ['strappy', 'slip-on', 'buckle'],
        'toe': ['open', 'peep-toe', 'closed'],
        'style': ['casual', 'business', 'semi-formal']
    },
    'boots': {
        'types': ['ankle boots', 'knee-high boots', 'riding boots', 'chelsea boots'],
        'heel_height': ['flat', 'low', 'medium'],
        'closure': ['zipper', 'lace-up', 'slip-on'],
        'toe': ['closed'],
        'style': ['casual', 'business', 'semi-formal']
    }
}

# Material and texture combinations with seasonal weighting
MATERIAL_COMBINATIONS = {
    'summer': {
        'cotton': 0.9,
        'linen': 0.9,
        'silk': 0.8,
        'light': 0.9,
        'bamboo': 0.8,
        'modal': 0.8,
        'synthetic': 0.3,  # Lower weight for synthetic in summer
        'wool': 0.1,
        'cashmere': 0.1,
        'velvet': 0.1,
        'fleece': 0.1
    },
    'winter': {
        'wool': 0.9,
        'cashmere': 0.9,
        'fleece': 0.9,
        'velvet': 0.8,
        'cotton': 0.6,
        'silk': 0.5,
        'synthetic': 0.7,
        'linen': 0.2,
        'light': 0.1,
        'bamboo': 0.3,
        'modal': 0.3
    },
    'spring': {
        'cotton': 0.8,
        'linen': 0.8,
        'silk': 0.8,
        'light': 0.7,
        'synthetic': 0.5,
        'wool': 0.4,
        'bamboo': 0.6,
        'modal': 0.6
    },
    'fall': {
        'wool': 0.8,
        'cotton': 0.7,
        'silk': 0.7,
        'synthetic': 0.6,
        'linen': 0.4,
        'light': 0.3,
        'bamboo': 0.4,
        'modal': 0.4
    }
}

# Appropriate materials for different item types
ITEM_MATERIALS = {
    'top': {
        'cotton': 0.9,
        'linen': 0.9,
        'silk': 0.8,
        'synthetic': 0.7,
        'wool': 0.6,
        'cashmere': 0.5,
        'denim': 0.4
    },
    'bottom': {
        'cotton': 0.9,
        'denim': 0.9,
        'synthetic': 0.8,
        'linen': 0.7,
        'wool': 0.6,
        'silk': 0.4,
        'leather': 0.5,
        'suede': 0.4
    },
    'shoes': {
        'leather': 0.9,
        'suede': 0.8,
        'synthetic': 0.7,
        'canvas': 0.7,
        'mesh': 0.6,
        'wool': 0.3,
        'silk': 0.2,
        'cotton': 0.2
    }
}

# Add legwear types and their seasonal appropriateness
LEGWEAR_TYPES = {
    'stockings': {
        'seasons': ['winter', 'fall'],
        'formality': ['formal', 'business'],
        'materials': ['nylon', 'silk', 'cotton']
    },
    'leggings': {
        'seasons': ['winter', 'fall', 'spring'],
        'formality': ['casual', 'business'],
        'materials': ['cotton', 'spandex', 'polyester']
    },
    'fishnets': {
        'seasons': ['summer', 'spring'],
        'formality': ['party', 'casual'],
        'materials': ['nylon']
    },
    'tights': {
        'seasons': ['winter', 'fall'],
        'formality': ['casual', 'business'],
        'materials': ['nylon', 'cotton', 'wool']
    },
    'shorts': {
        'seasons': ['summer', 'spring'],
        'formality': ['casual'],
        'materials': ['cotton', 'denim', 'linen']
    },
    'none': {
        'seasons': ['summer'],
        'formality': ['casual', 'party'],
        'materials': []
    }
}

# Add dress styles and their characteristics
DRESS_STYLES = {
    'casual': {
        'lengths': ['mini', 'midi'],
        'necklines': ['round', 'v-neck'],
        'sleeve_types': ['sleeveless', 'short-sleeve'],
        'materials': ['cotton', 'linen', 'denim']
    },
    'business': {
        'lengths': ['midi', 'knee-length'],
        'necklines': ['v-neck', 'round', 'collared'],
        'sleeve_types': ['short-sleeve', 'long-sleeve'],
        'materials': ['cotton', 'polyester', 'wool']
    },
    'formal': {
        'lengths': ['midi', 'maxi'],
        'necklines': ['v-neck', 'sweetheart', 'halter'],
        'sleeve_types': ['sleeveless', 'short-sleeve', 'long-sleeve'],
        'materials': ['silk', 'satin', 'lace']
    },
    'party': {
        'lengths': ['mini', 'midi'],
        'necklines': ['v-neck', 'sweetheart', 'halter'],
        'sleeve_types': ['sleeveless', 'short-sleeve'],
        'materials': ['silk', 'satin', 'sequin']
    }
}

def get_style_context(event_context: EventContext) -> str:
    """Get style context based on event type and formality level."""
    event_type = event_context.event_type.lower()
    formality_level = event_context.formality_level
    
    # Direct event type mappings
    if event_type in ['wedding', 'gala', 'black tie']:
        return 'formal'
    elif event_type in ['business', 'meeting', 'interview']:
        return 'business'
    elif event_type in ['party', 'cocktail']:
        return 'party'
    
    # Formality level mappings
    if formality_level >= 7:
        return 'formal'
    elif formality_level >= 4:
        return 'business'
    else:
        return 'casual'

def validate_material_for_season(material: str, season: str) -> bool:
    """Validate if a material is appropriate for the given season."""
    return material in MATERIAL_COMBINATIONS[season]

def get_material_context(event_context: EventContext) -> List[str]:
    """Get appropriate materials based on event context and season."""
    specs = MaterialSpecifications()
    season = event_context.season.lower()
    formality = get_style_context(event_context)
    
    # Get materials based on both season and formality
    materials = specs.recommend_materials(season, formality)
    
    # If no materials found, try getting just seasonal materials
    if not materials:
        materials = specs.get_materials_for_season(season)
    
    # If still no materials, use default materials based on formality
    if not materials:
        materials = specs.get_materials_for_formality(formality)
    
    # If still no materials, use safe defaults based on season
    if not materials:
        if season == 'winter':
            materials = ['wool', 'cashmere', 'fleece', 'velvet', 'leather', 'suede']
        elif season == 'summer':
            materials = ['cotton', 'linen', 'silk', 'bamboo', 'modal', 'mesh']
        elif season == 'spring':
            materials = ['cotton', 'linen', 'silk', 'bamboo', 'modal']
        elif season == 'fall':
            materials = ['wool', 'cotton', 'denim', 'leather', 'suede', 'velvet']
        else:
            materials = ['cotton', 'synthetic']
    
    # Ensure we have at least one material
    if not materials:
        materials = ['cotton', 'synthetic']
    
    return materials

def get_appropriate_shoe_type(event_context: EventContext, user_profile: UserProfile) -> ShoeDetails:
    """Get appropriate shoe type based on event context and user profile."""
    style_context = get_style_context(event_context)
    specs = MaterialSpecifications()
    
    # Get appropriate shoe types for the style context
    appropriate_types = []
    for shoe_type, details in SHOE_TYPES.items():
        if style_context in details['style']:
            appropriate_types.append(shoe_type)
    
    if not appropriate_types:
        raise ValueError(f"No appropriate shoe types found for {style_context} style")
    
    # Select a shoe type
    selected_type = random.choice(appropriate_types)
    shoe_details = SHOE_TYPES[selected_type]
    
    # Consider user's comfort level and special requirements
    comfort_level = user_profile.comfort_level
    special_requirement = user_profile.special_requirement
    
    # Adjust heel height based on comfort level and special requirements
    if special_requirement == SpecialRequirement.PREGNANT.value:
        heel_height = 'flat'
    elif comfort_level < 3:  # Low comfort level
        heel_height = random.choice(['flat', 'low'])
    else:
        heel_height = random.choice(shoe_details['heel_height'])
    
    # Select other attributes
    closure = random.choice(shoe_details['closure'])
    toe = random.choice(shoe_details['toe'])
    style = random.choice(shoe_details['style'])
    
    # Get appropriate material for shoes based on season
    season = event_context.season.lower()
    available_materials = specs.get_materials_for_season(season)
    shoe_materials = ['leather', 'suede', 'canvas', 'mesh', 'synthetic']
    seasonal_materials = [m for m in shoe_materials if m in available_materials]
    
    if not seasonal_materials:
        seasonal_materials = ['synthetic']  # Default to synthetic if no appropriate materials
    
    return ShoeDetails(
        type=random.choice(shoe_details['types']),
        heel_height=heel_height,
        closure=closure,
        toe=toe,
        style=style,
        material=random.choice(seasonal_materials)
    )

def generate_outfit_item(item_type: str, request: OutfitRequest, available_materials: List[str]) -> OutfitItem:
    """Generate an outfit item based on type and context."""
    style_context = get_style_context(request.event_context)
    specs = MaterialSpecifications()
    
    # Get style inspirations for the context
    inspirations = STYLE_INSPIRATIONS.get(style_context, STYLE_INSPIRATIONS['casual'])  # Default to casual if style not found
    available_styles = inspirations.get(f'{item_type}s', [])
    
    if not available_styles:
        # Fallback to casual styles if no styles found for the item type
        available_styles = STYLE_INSPIRATIONS['casual'].get(f'{item_type}s', [])
        if not available_styles:
            raise ValueError(f"No styles available for {item_type}")
    
    # Select style based on user preferences
    preferred_styles = [s for s in available_styles if s in request.user_profile.style_preferences]
    selected_style = random.choice(preferred_styles) if preferred_styles else random.choice(available_styles)
    
    # Select color based on user preferences
    preferred_colors = request.user_profile.color_preferences
    selected_color = random.choice(preferred_colors) if preferred_colors else 'neutral'
    
    # Get appropriate material from available materials
    if not available_materials:
        raise ValueError(f"No materials available for {request.event_context.season} season")
    
    # Weight materials based on item type and formality
    formality = get_style_context(request.event_context)
    formality_materials = set(specs.get_materials_for_formality(formality))
    weighted_materials = []
    
    for material in available_materials:
        if material in formality_materials:
            weighted_materials.append((material, 1.0))
        else:
            weighted_materials.append((material, 0.5))
    
    # Select material based on weights
    total_weight = sum(w for _, w in weighted_materials)
    if total_weight == 0:
        selected_material = 'synthetic'  # Fallback to synthetic if no appropriate materials
    else:
        r = random.uniform(0, total_weight)
        current_weight = 0
        selected_material = None
        for material, weight in weighted_materials:
            current_weight += weight
            if r <= current_weight:
                selected_material = material
                break
        if not selected_material:
            selected_material = available_materials[0]
    
    # Select fit based on user preferences and body type
    preferred_fits = request.user_profile.fit_preferences
    selected_fit = random.choice(preferred_fits) if preferred_fits else 'regular'
    
    return OutfitItem(
        type=item_type,
        color=selected_color,
        material=selected_material,
        fit=selected_fit,
        style=selected_style
    )

def get_appropriate_legwear(event_context: EventContext, user_profile: UserProfile) -> Optional[LegwearItem]:
    """Determine appropriate legwear based on context and user preferences."""
    season = event_context.season.lower()
    formality = get_style_context(event_context)
    
    # Get available legwear types for the season and formality
    available_types = [
        type_name for type_name, details in LEGWEAR_TYPES.items()
        if season in details['seasons'] and formality in details['formality']
    ]
    
    if not available_types:
        return None
    
    # Select legwear type
    selected_type = random.choice(available_types)
    if selected_type == 'none':
        return None
    
    # Get available materials for the selected type
    available_materials = LEGWEAR_TYPES[selected_type]['materials']
    selected_material = random.choice(available_materials)
    
    # Select color based on user preferences
    selected_color = random.choice(user_profile.color_preferences) if user_profile.color_preferences else 'black'
    
    # Create legwear item
    legwear = LegwearItem(
        type=selected_type,
        color=selected_color,
        material=selected_material
    )
    
    # Add optional properties based on type
    if selected_type in ['stockings', 'tights']:
        legwear.opacity = random.choice(['sheer', 'opaque', 'semi-opaque'])
    if selected_type == 'fishnets':
        legwear.pattern = random.choice(['diamond', 'hexagonal'])
    
    return legwear

def get_appropriate_dress(event_context: EventContext, user_profile: UserProfile) -> DressItem:
    """Generate an appropriate dress based on context and user preferences."""
    style_context = get_style_context(event_context)
    dress_style = DRESS_STYLES[style_context]
    
    # Select dress characteristics
    length = random.choice(dress_style['lengths'])
    neckline = random.choice(dress_style['necklines'])
    sleeve_type = random.choice(dress_style['sleeve_types'])
    
    # Get available materials
    available_materials = get_material_context(event_context)
    selected_material = random.choice(available_materials)
    
    # Select color based on user preferences
    selected_color = random.choice(user_profile.color_preferences) if user_profile.color_preferences else 'black'
    
    # Select fit based on user preferences
    selected_fit = random.choice(user_profile.fit_preferences) if user_profile.fit_preferences else 'regular'
    
    return DressItem(
        type='dress',
        color=selected_color,
        material=selected_material,
        fit=selected_fit,
        style=style_context,
        length=length,
        neckline=neckline,
        sleeve_type=sleeve_type
    )

def should_use_dress(event_context: EventContext, user_profile: UserProfile) -> bool:
    """Determine if a dress should be used instead of top+bottom."""
    # Higher probability for formal events
    if event_context.formality_level >= 7:
        return random.random() < 0.7
    
    # Higher probability for summer
    if event_context.season.lower() == 'summer':
        return random.random() < 0.6
    
    # Higher probability for party events
    if event_context.event_type.lower() in ['party', 'cocktail', 'wedding']:
        return random.random() < 0.8
    
    # Base probability
    return random.random() < 0.3

@app.post("/api/generate/top")
async def generate_top(request: Dict):
    """Generate a top based on user profile and event context."""
    try:
        outfit_request = OutfitRequest.from_dict(request)
        available_materials = get_material_context(outfit_request.event_context)
        top = generate_outfit_item('top', outfit_request, available_materials)
        return {"top": top}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/bottom")
async def generate_bottom(request: Dict):
    """Generate a bottom based on user profile and event context."""
    try:
        outfit_request = OutfitRequest.from_dict(request)
        available_materials = get_material_context(outfit_request.event_context)
        bottom = generate_outfit_item('bottom', outfit_request, available_materials)
        return {"bottom": bottom}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/shoes")
async def generate_shoes(request: Dict):
    """Generate shoes based on user profile and event context."""
    try:
        # Validate request structure
        if not isinstance(request, dict):
            raise HTTPException(status_code=400, detail="Request must be a dictionary")
        if 'user_profile' not in request or 'event_context' not in request:
            raise HTTPException(status_code=400, detail="Request must contain user_profile and event_context")
        
        # Create OutfitRequest
        try:
            outfit_request = OutfitRequest.from_dict(request)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid request format: {str(e)}")
        
        # Generate shoes
        try:
            shoes = get_appropriate_shoe_type(outfit_request.event_context, outfit_request.user_profile)
            return {"shoes": shoes.model_dump()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating shoes: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/complete-outfit", response_model=CompleteOutfitResponse)
async def generate_complete_outfit(request: Dict):
    """Generate a complete outfit based on user profile and event context."""
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info(f"Starting complete outfit generation (Request ID: {request_id})")
    
    try:
        # Validate request structure
        if not isinstance(request, dict):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid request format",
                    "message": "Request must be a dictionary",
                    "request_id": request_id
                }
            )
        
        if 'user_profile' not in request or 'event_context' not in request:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Missing required fields",
                    "message": "Request must contain user_profile and event_context",
                    "request_id": request_id
                }
            )
        
        # Create OutfitRequest
        try:
            outfit_request = OutfitRequest.from_dict(request)
            logger.debug(f"Created OutfitRequest (Request ID: {request_id}): {outfit_request.model_dump()}")
        except ValidationError as e:
            logger.error(f"Validation error (Request ID: {request_id}): {str(e)}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Validation error",
                    "message": str(e),
                    "request_id": request_id
                }
            )
        
        # Get available materials
        try:
            available_materials = get_material_context(outfit_request.event_context)
            logger.debug(f"Available materials (Request ID: {request_id}): {available_materials}")
        except MaterialSelectionError as e:
            logger.error(f"Material selection error (Request ID: {request_id}): {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Material selection error",
                    "message": str(e),
                    "request_id": request_id
                }
            )
        
        try:
            # Decide whether to use dress or top+bottom
            use_dress = should_use_dress(outfit_request.event_context, outfit_request.user_profile)
            
            if use_dress:
                logger.debug(f"Generating dress (Request ID: {request_id})...")
                dress = get_appropriate_dress(outfit_request.event_context, outfit_request.user_profile)
                logger.debug(f"Generated dress (Request ID: {request_id}): {dress.model_dump()}")
                
                logger.debug(f"Generating legwear (Request ID: {request_id})...")
                legwear = get_appropriate_legwear(outfit_request.event_context, outfit_request.user_profile)
                logger.debug(f"Generated legwear (Request ID: {request_id}): {legwear.model_dump() if legwear else None}")
                
                top = None
                bottom = None
            else:
                logger.debug(f"Generating top (Request ID: {request_id})...")
                top = generate_outfit_item('top', outfit_request, available_materials)
                logger.debug(f"Generated top (Request ID: {request_id}): {top.model_dump()}")
                
                logger.debug(f"Generating bottom (Request ID: {request_id})...")
                bottom = generate_outfit_item('bottom', outfit_request, available_materials)
                logger.debug(f"Generated bottom (Request ID: {request_id}): {bottom.model_dump()}")
                
                dress = None
                legwear = None
            
            logger.debug(f"Generating shoes (Request ID: {request_id})...")
            shoes = get_appropriate_shoe_type(outfit_request.event_context, outfit_request.user_profile)
            logger.debug(f"Generated shoes (Request ID: {request_id}): {shoes.model_dump()}")
            
            # Create complete outfit response
            outfit = OutfitResponse(
                style_preferences=outfit_request.user_profile.style_preferences,
                color_preferences=outfit_request.user_profile.color_preferences,
                materials=available_materials,
                suitability='appropriate',
                occasion=outfit_request.event_context.event_type,
                season=outfit_request.event_context.season,
                formality_level=outfit_request.event_context.formality_level,
                comfort_level=outfit_request.user_profile.comfort_level,
                top=top,
                bottom=bottom,
                dress=dress,
                legwear=legwear,
                shoes=shoes
            )
            logger.info(f"Successfully generated complete outfit (Request ID: {request_id})")
            
            return CompleteOutfitResponse(outfit=outfit)
            
        except OutfitGenerationError as e:
            logger.error(f"Outfit generation error (Request ID: {request_id}): {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Outfit generation error",
                    "message": str(e),
                    "request_id": request_id
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_complete_outfit (Request ID: {request_id}): {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unexpected error",
                "message": str(e),
                "request_id": request_id
            }
        )

@app.post("/api/measurements/validate")
async def validate_measurements(profile: Dict):
    """Validate user measurements and return detailed feedback."""
    try:
        validator = MeasurementValidation()
        is_valid, errors = validator.validate_measurements(profile)
        
        if is_valid:
            return {
                'valid': True,
                'message': 'All measurements are valid'
            }
        else:
            return {
                'valid': False,
                'errors': errors
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/measurements/estimate")
async def estimate_measurements(profile: Dict):
    """Estimate missing measurements based on provided ones."""
    try:
        estimator = MeasurementEstimator()
        
        # Ensure we have at least the basic measurements
        required_measurements = ['height', 'weight', 'bust']
        if not all(key in profile for key in required_measurements):
            raise HTTPException(
                status_code=400,
                detail=f"Missing required measurements. Please provide at least: {', '.join(required_measurements)}"
            )
        
        # Estimate missing measurements
        estimated = estimator.estimate_missing_measurements(profile)
        
        # Validate the estimated measurements
        validator = MeasurementValidation()
        is_valid, errors = validator.validate_measurements(estimated)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Could not generate valid measurements: {errors}")

        # Identify which measurements were estimated
        estimated_fields = {
            key: {
                'value': value,
                'was_estimated': key not in profile
            }
            for key, value in estimated.items()
        }

        return {
            'measurements': estimated_fields,
            'body_type': estimated['body_type']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/measurements/guide")
async def get_measurement_guide():
    """Get a guide for taking measurements."""
    try:
        guide = {
            "height": "Measure from top of head to feet",
            "weight": "Measure total body weight",
            "bust": "Measure around the fullest part of the bust",
            "waist": "Measure around the natural waistline",
            "hips": "Measure around the fullest part of the hips",
            "inseam": "Measure from crotch to desired length",
            "shoulder_width": "Measure across the back from shoulder to shoulder",
            "arm_length": "Measure from shoulder to wrist"
        }
        
        return {
            'guide': guide,
            'default_measurements': MeasurementEstimator.DEFAULT_MEASUREMENTS,
            'valid_ranges': {
                key: {
                    'min': range_info.min_value,
                    'max': range_info.max_value,
                    'unit': range_info.unit,
                    'description': range_info.description
                }
                for key, range_info in MeasurementEstimator.MEASUREMENT_RANGES.items()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/measurements/body-type")
async def determine_body_type(profile: Dict):
    """Determine body type based on provided measurements."""
    try:
        estimator = MeasurementEstimator()
        estimated = estimator.estimate_missing_measurements(profile)
        
        # Get body type characteristics
        body_type = BodyType(estimated['body_type'])
        characteristics = MeasurementEstimator.BODY_TYPE_CHARACTERISTICS[body_type]

        return {
            'body_type': body_type.value,
            'characteristics': {
                'waist_to_hip_ratio': characteristics['waist_to_hip_ratio'],
                'bust_to_hip_ratio': characteristics['bust_to_hip_ratio'],
                'shoulder_to_hip_ratio': characteristics['shoulder_to_hip_ratio']
            },
            'measurements': estimated
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/materials")
async def get_materials():
    """Get all available materials and their properties."""
    specs = MaterialSpecifications()
    return specs.material_properties

@app.get("/api/textures")
async def get_textures():
    """Get all available textures and their properties."""
    specs = MaterialSpecifications()
    return specs.texture_properties

@app.get("/api/material-combinations")
async def get_material_combinations():
    """Get all available material combinations and their properties."""
    specs = MaterialSpecifications()
    return specs.material_combinations

# Add middleware for request logging and error handling
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    # Log request
    logger.info(f"Request {request_id} started: {request.method} {request.url}")
    try:
        # Get request body if it exists
        body = await request.body()
        if body:
            try:
                body_json = json.loads(body)
                logger.debug(f"Request {request_id} body: {json.dumps(body_json, indent=2)}")
            except json.JSONDecodeError:
                logger.debug(f"Request {request_id} body: {body}")
    except Exception as e:
        logger.warning(f"Error reading request body: {e}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"Request {request_id} completed in {process_time:.2f}s with status {response.status_code}")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request {request_id} failed after {process_time:.2f}s: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(e),
                "request_id": request_id
            }
        )

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host="127.0.0.1", port=5001, log_level="debug")
    except Exception as e:
        print(f"Error starting server: {str(e)}") 