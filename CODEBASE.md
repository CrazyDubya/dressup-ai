# Outfit Generator Codebase Documentation

## Dependencies
```requirements.txt
fastapi
uvicorn
pydantic
requests
```

## API Module (`api.py`)

### Pydantic Models
- `UserProfile`: User measurements and preferences
  - Properties: height, weight, bust, waist, hips, inseam, shoe_size, comfort_level, style_preferences, color_preferences, fit_preferences
  - Methods: `from_dict(data: Dict) -> UserProfile`

- `EventContext`: Event details and conditions
  - Properties: event_type, formality_level, weather_conditions, time_of_day, season, location, duration, activity_level
  - Methods: `from_dict(data: Dict) -> EventContext`

- `OutfitRequest`: Combined request model
  - Properties: user_profile (UserProfile), event_context (EventContext)
  - Methods: `from_dict(data: Dict) -> OutfitRequest`

- `OutfitItem`: Individual clothing item
  - Properties: type, color, material, fit, style

- `ShoeDetails`: Shoe-specific details
  - Properties: type, heel_height, closure, toe, style, material

- `OutfitResponse`: Complete outfit response
  - Properties: style_preferences, color_preferences, materials, suitability, occasion, season, formality_level, comfort_level, top, bottom, shoes

- `CompleteOutfitResponse`: Wrapper for outfit response
  - Properties: outfit (OutfitResponse)

### Helper Functions
- `get_style_context(event_context: EventContext) -> str`
  - Determines style based on formality level
  - Returns: 'formal' or 'casual'

- `validate_material_for_season(material: str, season: str) -> bool`
  - Checks if material is appropriate for season
  - Returns: True if valid, False otherwise

- `get_material_context(event_context: EventContext) -> List[str]`
  - Gets appropriate materials based on event context
  - Returns: List of suitable materials

- `get_appropriate_material(item_type: str, available_materials: List[str], season: str) -> str`
  - Selects appropriate material with seasonal validation
  - Returns: Selected material name

- `get_appropriate_shoe_type(event_context: EventContext, user_profile: UserProfile) -> ShoeDetails`
  - Determines appropriate shoe type based on context
  - Returns: ShoeDetails object

- `generate_outfit_item(item_type: str, request: OutfitRequest, available_materials: List[str]) -> OutfitItem`
  - Generates single outfit item with material restrictions
  - Returns: OutfitItem object

### API Endpoints
- `POST /api/generate/top`: Generate top only
- `POST /api/generate/bottom`: Generate bottom only
- `POST /api/generate/shoes`: Generate shoes only
- `POST /api/generate/complete-outfit`: Generate complete outfit

## Dress Maker Module (`dress_maker.py`)

### Pydantic Models
- `OutfitComponent`: Detailed clothing component
  - Properties: type, color, material, fit, style, hem, bust_fit, shoulder_fit, arm_fit, waist_fit, hip_fit, length

- `OutfitData`: Complete outfit data
  - Properties: top, bottom, shoes, extras, style, colors, materials, suitable_for, occasion, season, formality_level, comfort_level

### DressMaker Class
- `__init__()`: Initializes style variations for casual and formal wear

- `_generate_outfit_data(event: str, outfit_number: int, variation: int, is_character_outfit: bool, character_context: Optional[Dict], real_world_context: Optional[Dict], style_expression: Optional[str], user_name: Optional[str]) -> OutfitData`
  - Generates complete outfit data based on parameters
  - Returns: OutfitData object

- `generate_outfit(event: str, num_outfits: int, variations_per_outfit: int, is_character_outfit: bool = False, character_context: Optional[Dict] = None, real_world_context: Optional[Dict] = None, style_expression: Optional[str] = None, user_name: Optional[str] = None, max_retries: int = 3) -> List[OutfitData]`
  - Main outfit generation function with retry logic
  - Returns: List of OutfitData objects

- `_get_missing_components(outfit_data: OutfitData) -> List[str]`
  - Checks for missing required components
  - Returns: List of missing component names

- `_generate_missing_component(component: str, outfit_data: OutfitData) -> Optional[Dict]`
  - Generates missing component based on existing outfit
  - Returns: Component data dictionary

- `_validate_outfit_data(outfit_data: OutfitData) -> bool`
  - Validates completeness of outfit data
  - Returns: True if valid, False otherwise

## Test Module (`test_outfits.py`)

### Material Properties
- `MATERIAL_PROPERTIES`: Dictionary defining material characteristics
- `WEATHER_FACTORS`: Dictionary defining weather impact on materials

### Test Functions
- `calculate_material_weight(material: str, item_type: str, season: str, weather: List[str], event_type: str, formality: int) -> float`
  - Calculates material suitability weight
  - Returns: Weight value between 0 and 1

- `validate_material_for_season(material: str, season: str) -> bool`
  - Validates seasonal appropriateness
  - Returns: True if valid, False otherwise

- `get_weighted_material(item_type: str, season: str, event_type: str, weather: List[str], formality: int, available_materials: List[str]) -> str`
  - Selects material based on weighted factors
  - Returns: Selected material name

- `generate_test_contexts(num_tests: int = 1000) -> List[OutfitRequest]`
  - Generates test data
  - Returns: List of OutfitRequest objects

- `analyze_outfit(outfit: Dict) -> Dict`
  - Analyzes generated outfit
  - Returns: Analysis dictionary

- `run_outfit_tests()`
  - Main test runner function
  - Prints test results and statistics

## Client Interface (`client.html`)

### JavaScript Functions
- `updateProfile()`: Updates user profile in localStorage
- `getEventContext()`: Gets current event context from form
- `showLoading()`: Shows loading indicator
- `hideLoading()`: Hides loading indicator
- `getUserProfile()`: Gets user profile from form
- `displayResults(response)`: Displays outfit results
- `generateOutfit()`: Calls API to generate complete outfit
- `generateTop()`: Calls API to generate top only
- `generateBottom()`: Calls API to generate bottom only
- `generateShoes()`: Calls API to generate shoes only
- `initializeForm()`: Initializes form with default values

### Form Components
- User Profile Section: Measurements and preferences
- Event Context Section: Event details and conditions
- Generate Outfit Section: Generation buttons and results display

## Constants and Configuration

### Style Inspirations
- Casual and formal variations for tops, bottoms, and shoes

### Shoe Types
- Detailed definitions for different shoe types and their attributes

### Material Combinations
- Seasonal weightings for different materials

### Item Materials
- Appropriate materials for different item types with weightings 