# DressUp - AI-Powered Outfit Generator

An intelligent outfit generation system that creates personalized outfits based on user measurements, preferences, and event context.

## Features

- 🎯 Personalized outfit generation based on user measurements
- 🌡️ Season and weather-aware material selection
- 👔 Formality level consideration with event-type mapping
- 🎨 Style and color preference integration
- 👗 Support for both separates (top+bottom) and dresses
- 🦵 Intelligent legwear generation for dresses
- 👞 Intelligent shoe matching with heel height adaptation
- 📏 Measurement validation and estimation
- 🎭 Special requirement handling (e.g., pregnancy considerations)
- 🔍 Comprehensive request logging and error handling

## Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/CrazyDubya/dressup-ai.git
cd dressup-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the server:
```bash
python api.py
```

The API will be available at http://localhost:5001

### API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:5001/docs
- ReDoc: http://localhost:5001/redoc

## API Endpoints

### Generate Complete Outfit
```http
POST /api/generate/complete-outfit
```

Generates a complete outfit (dress OR top+bottom) with shoes and optional legwear based on user profile and event context.

**Request Body:**
```json
{
  "user_profile": {
    "height": 170,
    "weight": 65,
    "bust": 90,
    "waist": 70,
    "hips": 95,
    "inseam": 80,
    "shoe_size": 38,
    "comfort_level": 8,
    "style_preferences": ["casual", "comfortable"],
    "color_preferences": ["blue", "gray", "black"],
    "fit_preferences": ["relaxed", "comfortable"],
    "special_requirement": "pregnant"
  },
  "event_context": {
    "event_type": "wedding",
    "formality_level": 8,
    "weather_conditions": ["cold"],
    "time_of_day": "evening",
    "season": "winter",
    "location": "indoor",
    "duration": 4,
    "activity_level": 2
  }
}
```

**Response:**
```json
{
  "outfit": {
    "style_preferences": ["casual", "comfortable"],
    "color_preferences": ["blue", "gray", "black"],
    "materials": ["wool", "cashmere", "fleece", "velvet", "cotton", "silk", "synthetic"],
    "suitability": "appropriate",
    "occasion": "wedding",
    "season": "winter",
    "formality_level": 8,
    "comfort_level": 8,
    "top": null,
    "bottom": null,
    "dress": {
      "type": "dress",
      "color": "blue",
      "material": "silk",
      "fit": "relaxed",
      "style": "formal",
      "length": "midi",
      "neckline": "v-neck",
      "sleeve_type": "long-sleeve"
    },
    "legwear": {
      "type": "tights",
      "material": "wool",
      "color": "black",
      "style": "formal"
    },
    "shoes": {
      "type": "flats",
      "heel_height": "flat",
      "closure": "slip-on",
      "toe": "closed",
      "style": "formal",
      "material": "leather"
    }
  },
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Generate Individual Items
- `POST /api/generate/top` - Generate top only
- `POST /api/generate/bottom` - Generate bottom only
- `POST /api/generate/shoes` - Generate shoes only

### Measurement Endpoints
- `POST /api/measurements/validate` - Validate user measurements
- `POST /api/measurements/estimate` - Estimate missing measurements
- `GET /api/measurements/guide` - Get measurement guide
- `POST /api/measurements/body-type` - Determine body type

### Material Information
- `GET /api/materials` - Get available materials
- `GET /api/textures` - Get available textures

### Haute Couture Profiles
- `GET /api/profiles` - Get available haute couture profiles
- `GET /api/profile/{profile_name}` - Get specific profile details
- `POST /api/generate/outfit` - Generate haute couture outfit

## Key Features

### Event-Based Formality Mapping
The system automatically adjusts formality levels based on event types:
- **Wedding/Formal**: Formality 7-9 (High chance of dress generation)
- **Business Meeting**: Formality 5-7 
- **Party**: Formality 3-5
- **Casual Gathering**: Formality 1-3

### Seasonal Material Selection
Materials are automatically selected based on season:
- **Summer**: Cotton, linen, silk, light fabrics, bamboo, modal, synthetic
- **Winter**: Wool, cashmere, fleece, velvet, cotton, silk, synthetic
- **Spring**: Cotton, linen, silk, light fabrics, synthetic, bamboo, modal
- **Fall**: Wool, cotton, silk, synthetic, linen, light fabrics, bamboo, modal

### Intelligent Dress vs. Separates Logic
- Formal events (7+): 60% chance of dress
- Semi-formal events (5-6): 40% chance of dress  
- Business events (4): 20% chance of dress
- Casual events (≤3): 10% chance of dress

### Smart Legwear Generation
Legwear is generated contextually:
- **Winter dresses**: Tights, stockings, or leggings
- **Fall dresses**: Tights, stockings (formal) or leggings (casual)
- **Spring formal dresses**: Stockings or tights
- **Summer formal dresses**: Optional stockings or fishnets

### Special Requirements Support
- **Pregnancy**: Automatically selects flat shoes and comfortable fits
- **Additional requirements**: Extensible system for future needs

## Development

### Project Structure

```
dressup-ai/
├── api.py                    # Main FastAPI application with outfit generation
├── measurement_endpoints.py  # Measurement-related API endpoints
├── measurement_utils.py      # Measurement estimation and validation utilities
├── measurement_validation.py # Input validation for measurements
├── material_specs.py         # Material and texture specifications
├── haute_couture_api.py      # Haute couture profile system
├── haute_couture_profiles.py # Profile management
├── dress_maker.py           # Legacy outfit generation (superseded by api.py)
├── test_api.py              # Comprehensive API tests (22 tests)
├── requirements.txt         # Project dependencies
├── docs/                    # Documentation
│   ├── api/                # API documentation
│   └── examples/           # Example requests/responses
└── README.md               # This file
```

### Running Tests

```bash
# Run the main API test suite (22 tests)
python -m pytest test_api.py -v

# Run specific test categories
python -m pytest test_api.py::test_generate_complete_outfit -v
python -m pytest test_api.py::test_dress_generation -v
python -m pytest test_api.py::test_seasonal_materials -v
```

### Error Handling

The API provides comprehensive error handling:
- **400 Bad Request**: Validation errors (invalid measurements, missing fields)
- **422 Unprocessable Entity**: Request format errors (converted to 400 with custom handler)
- **500 Internal Server Error**: Material selection errors, server issues

All error responses include:
```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "request_id": "unique-request-identifier"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all tests pass: `python -m pytest test_api.py`
5. Commit your changes
6. Push to the branch
7. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 