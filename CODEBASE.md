# DressUp AI Codebase Documentation

## Architecture Overview

The DressUp AI system is built as a FastAPI-based microservice architecture with modular components for outfit generation, measurements, materials, and haute couture profiles.

## Core Dependencies
```requirements.txt
fastapi==0.104.1          # Web framework
uvicorn==0.24.0           # ASGI server
pydantic==2.5.2           # Data validation
requests>=2.31.0          # HTTP client
numpy==1.26.2             # Numerical operations
pandas==2.1.3             # Data manipulation
scikit-learn==1.3.2       # Machine learning
matplotlib>=3.4.0         # Plotting
seaborn>=0.13.2           # Statistical plotting
python-multipart==0.0.6   # Form data handling
aiofiles==23.2.1          # Async file operations
pillow==10.1.0            # Image processing
pytest==7.4.3             # Testing framework
```

## Main API Module (`api.py`)

### Core Models

#### Request Models
- **`UserProfile`**: User measurements, preferences, and special requirements
  - Basic measurements: height, weight, bust, waist, hips, inseam, shoe_size
  - Preferences: style_preferences, color_preferences, fit_preferences
  - Special requirements: special_requirement (e.g., "pregnant")
  - Comfort settings: comfort_level (1-10)

- **`EventContext`**: Event details and environmental conditions
  - Event information: event_type, formality_level, time_of_day, location
  - Environmental: season, weather_conditions, duration, activity_level

- **`SimpleOutfitRequest`**: Combined request for individual item generation
  - Properties: user_profile (UserProfile), event_context (EventContext)

#### Response Models
- **`OutfitItem`**: Individual clothing piece
  - Properties: type, color, material, fit, style

- **`DressDetails`**: Dress-specific information
  - Properties: type, color, material, fit, style, length, neckline, sleeve_type

- **`LegwearDetails`**: Legwear specifications
  - Properties: type, material, color, style

- **`ShoeDetails`**: Shoe-specific details
  - Properties: type, heel_height, closure, toe, style, material

- **`OutfitResponse`**: Complete outfit with all components
  - Metadata: style_preferences, color_preferences, materials, suitability
  - Context: occasion, season, formality_level, comfort_level
  - Components: top, bottom, dress, legwear, shoes (Optional fields for dress vs separates)

- **`CompleteOutfitResponse`**: API response wrapper
  - Properties: outfit (OutfitResponse), request_id (string)

### Core Functions

#### Validation Functions
- **`validate_user_profile(profile: UserProfile) -> List[str]`**
  - Validates measurement ranges (height: 100-250cm, weight: 30-200kg, etc.)
  - Returns list of validation errors

- **`validate_event_context(context: EventContext) -> List[str]`**
  - Validates formality and activity levels (1-10 range)
  - Note: Season validation moved to material selection for proper error handling

#### Outfit Generation Logic
- **`get_formality_level_for_event(event_type: str, base_formality: Optional[int]) -> int`**
  - Maps event types to appropriate formality levels
  - Wedding/formal: 8, business: 6, party: 5, casual: 3, workout: 1

- **`get_style_context(event_context: EventContext) -> str`**
  - Determines style category based on formality
  - Returns: 'formal' (6+), 'business' (4-5), or 'casual' (<4)

- **`get_material_context(event_context: EventContext) -> List[str]`**
  - Selects seasonal materials with validation
  - Raises ValueError for invalid seasons (triggers 500 error)

- **`generate_dress(request: SimpleOutfitRequest, available_materials: List[str]) -> DressDetails`**
  - Generates dress with contextual attributes
  - Length selection based on formality (formal: midi/maxi, casual: mini/knee)
  - Neckline and sleeve selection based on season and formality

- **`generate_legwear(request: SimpleOutfitRequest, has_dress: bool) -> Optional[LegwearDetails]`**
  - Contextual legwear generation for dresses
  - Season-based rules: winter/fall require legwear, summer optional
  - Type selection: stockings (formal), tights (cold), leggings (casual)

- **`get_appropriate_shoe_type(event_context: EventContext, user_profile: UserProfile) -> ShoeDetails`**
  - Intelligent shoe selection with special requirement handling
  - Pregnancy consideration: forces flat heel height
  - Formality-based type selection: heels (formal), flats (business), sneakers (casual)

### API Endpoints

#### Outfit Generation Endpoints
- **`POST /api/generate/complete-outfit`**: Main outfit generation
  - Advanced dress vs. separates decision logic
  - Formality-based dress probability: formal 60%, semi-formal 40%, business 20%, casual 10%
  - Comprehensive error handling with request_id tracking

- **`POST /api/generate/top`**: Individual top generation
- **`POST /api/generate/bottom`**: Individual bottom generation  
- **`POST /api/generate/shoes`**: Individual shoe generation

#### Error Handling System
- **Custom Exception Handler**: Converts FastAPI 422 errors to 400 with request_id
- **Validation Errors (400)**: User input validation failures
- **Material Selection Errors (500)**: Invalid season processing
- **Request Logging**: All requests logged with unique request_id

## Measurement System (`measurement_*.py`)

### Measurement Endpoints (`measurement_endpoints.py`)
- **`POST /api/measurements/validate`**: Comprehensive measurement validation
- **`POST /api/measurements/estimate`**: AI-powered missing measurement estimation
- **`GET /api/measurements/guide`**: Interactive measurement guide
- **`POST /api/measurements/body-type`**: Body type classification

### Measurement Utilities (`measurement_utils.py`)
- **`MeasurementEstimator`**: Machine learning-based measurement prediction
- **`BodyType`**: Enum for body type classification
- **`SpecialRequirement`**: Enum for special needs (pregnancy, etc.)

### Validation (`measurement_validation.py`)
- **`MeasurementValidation`**: Rule-based measurement validation
- Comprehensive range checking and relationship validation

## Material System (`material_*.py`)

### Material Specifications (`material_specs.py`)
- **`MaterialSpecifications`**: Comprehensive material database
- **`MaterialDetail`**: Detailed material properties and characteristics
- **`TextureDetail`**: Texture information and applications
- **`FabricCombination`**: Material combination rules and recommendations

### Material Models (`material_models.py`)
- **`HauteCoutureProfile`**: High-end fashion profile system
- **`HauteCoutureDesign`**: Complete design specifications
- Advanced material and construction modeling

## Haute Couture System

### Profile Management (`haute_couture_profiles.py`)
- **`get_profile(name: str)`**: Retrieve specific haute couture profiles
- **`list_profiles()`**: Get available profile names
- **`get_profile_details(name: str)`**: Detailed profile information

### API Integration (`haute_couture_api.py`)
- Advanced haute couture outfit generation
- Premium material and construction specifications
- Custom timeline and cost modeling

## Testing Infrastructure

### Main Test Suite (`test_api.py`)
**22 comprehensive tests covering:**

#### Core Functionality Tests (6 tests)
- Measurement validation and estimation
- Body type determination
- Measurement guide retrieval

#### Outfit Generation Tests (8 tests)
- Individual item generation (top, bottom, shoes)
- Complete outfit generation
- Special requirements handling (pregnancy)
- Seasonal material selection
- Style context mapping

#### Advanced Feature Tests (5 tests)
- Dress generation for formal events
- Legwear generation for winter/formal contexts
- Summer dress handling (no legwear)
- Dress+legwear combinations
- Massive outfit generation (4000 outfits with statistical analysis)

#### Error Handling Tests (3 tests)
- Request format validation
- Input validation error responses
- Material selection error handling
- Request logging verification

### Test Configuration
- **Comprehensive Test Data**: Realistic user profiles and event contexts
- **Statistical Validation**: Dress ratio analysis (20-80% expected range)
- **Seasonal Testing**: All four seasons with appropriate material validation
- **Error Response Validation**: Proper HTTP status codes and error formats

## Constants and Configuration

### Seasonal Material Mapping
```python
MATERIAL_COMBINATIONS = {
    'summer': ['cotton', 'linen', 'silk', 'light', 'bamboo', 'modal', 'synthetic'],
    'winter': ['wool', 'cashmere', 'fleece', 'velvet', 'cotton', 'silk', 'synthetic'],
    'spring': ['cotton', 'linen', 'silk', 'light', 'synthetic', 'bamboo', 'modal'],
    'fall': ['wool', 'cotton', 'silk', 'synthetic', 'linen', 'light', 'bamboo', 'modal']
}
```

### Legwear Compatibility
```python
LEGWEAR_TYPES = {
    'stockings': {'seasons': ['winter', 'fall', 'spring', 'summer']},
    'tights': {'seasons': ['winter', 'fall', 'spring']},
    'leggings': {'seasons': ['winter', 'fall', 'spring']},
    'fishnets': {'seasons': ['summer', 'spring']},
    'none': {'seasons': ['summer', 'spring', 'fall', 'winter']}
}
```

## Performance Characteristics

### Response Times
- Individual item generation: ~100-200ms
- Complete outfit generation: ~200-500ms
- Measurement validation: ~50-100ms
- 4000 outfit generation test: ~8-10 seconds

### Scalability Features
- Async FastAPI endpoints for concurrent request handling
- Stateless design for horizontal scaling
- Comprehensive logging for monitoring and debugging
- Request ID tracking for distributed tracing

## Development Workflow

### Code Quality Standards
- Type hints throughout codebase
- Pydantic models for data validation
- Comprehensive error handling
- Request/response logging
- 100% API test coverage

### Deployment Considerations
- FastAPI with uvicorn for production deployment
- Environment-based configuration
- Health check endpoints
- Prometheus metrics integration ready
- Docker containerization support

## Future Enhancement Areas

### Planned Improvements
1. **AI/ML Integration**: Advanced style learning from user feedback
2. **Image Generation**: Visual outfit rendering
3. **Inventory Integration**: Real product database connectivity
4. **Social Features**: Outfit sharing and rating system
5. **Mobile Optimization**: Mobile-specific UI/UX considerations 