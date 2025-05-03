# DressUp - AI-Powered Outfit Generator

An intelligent outfit generation system that creates personalized outfits based on user measurements, preferences, and event context.

## Features

- 🎯 Personalized outfit generation based on user measurements
- 🌡️ Season and weather-aware material selection
- 👔 Formality level consideration
- 🎨 Style and color preference integration
- 👗 Support for both separates and dresses
- 👞 Intelligent shoe matching
- 📏 Measurement validation and estimation

## Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dressup.git
cd dressup
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

Generates a complete outfit based on user profile and event context.

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
    "fit_preferences": ["relaxed", "comfortable"]
  },
  "event_context": {
    "event_type": "casual",
    "formality_level": 2,
    "weather_conditions": ["cold"],
    "time_of_day": "day",
    "season": "winter",
    "location": "outdoor",
    "duration": 2,
    "activity_level": 3
  }
}
```

**Response:**
```json
{
  "outfit": {
    "style_preferences": ["casual", "comfortable"],
    "color_preferences": ["blue", "gray", "black"],
    "materials": ["wool", "cashmere", "fleece"],
    "suitability": "appropriate",
    "occasion": "casual",
    "season": "winter",
    "formality_level": 2,
    "comfort_level": 8,
    "top": {
      "type": "sweater",
      "color": "blue",
      "material": "wool",
      "fit": "relaxed",
      "style": "casual"
    },
    "bottom": {
      "type": "pants",
      "color": "gray",
      "material": "wool",
      "fit": "comfortable",
      "style": "casual"
    },
    "shoes": {
      "type": "boots",
      "heel_height": "low",
      "closure": "lace-up",
      "toe": "closed",
      "style": "casual",
      "material": "leather"
    }
  }
}
```

### Other Endpoints

- `POST /api/generate/top` - Generate top only
- `POST /api/generate/bottom` - Generate bottom only
- `POST /api/generate/shoes` - Generate shoes only
- `POST /api/measurements/validate` - Validate user measurements
- `POST /api/measurements/estimate` - Estimate missing measurements
- `GET /api/measurements/guide` - Get measurement guide
- `POST /api/measurements/body-type` - Determine body type
- `GET /api/materials` - Get available materials
- `GET /api/textures` - Get available textures
- `GET /api/material-combinations` - Get material combinations

## Development

### Project Structure

```
dressup/
├── api.py              # FastAPI application
├── material_specs.py   # Material specifications
├── dress_maker.py      # Outfit generation logic
├── test_api.py         # API tests
├── test_outfits.py     # Outfit generation tests
├── requirements.txt    # Project dependencies
├── docs/              # Documentation
│   ├── api/          # API documentation
│   └── examples/     # Example requests/responses
└── README.md         # This file
```

### Running Tests

```bash
python -m pytest test_api.py test_outfits.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 