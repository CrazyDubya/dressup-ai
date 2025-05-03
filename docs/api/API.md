# DressUp API Documentation

## Overview

The DressUp API provides endpoints for generating personalized outfits based on user measurements, preferences, and event context. The API is RESTful and returns JSON responses.

## Base URL

```
http://localhost:5001
```

## Authentication

Currently, the API does not require authentication. Future versions may implement OAuth2 or API key authentication.

## Endpoints

### Generate Complete Outfit

Generates a complete outfit (top, bottom, and shoes) based on user profile and event context.

```http
POST /api/generate/complete-outfit
```

#### Request Body

| Field | Type | Description |
|-------|------|-------------|
| user_profile | object | User's physical measurements and preferences |
| event_context | object | Event details and environmental conditions |

##### user_profile Object

| Field | Type | Description |
|-------|------|-------------|
| height | number | Height in centimeters |
| weight | number | Weight in kilograms |
| bust | number | Bust measurement in centimeters |
| waist | number | Waist measurement in centimeters |
| hips | number | Hip measurement in centimeters |
| inseam | number | Inseam measurement in centimeters |
| shoe_size | number | Shoe size in EU sizing |
| comfort_level | number | Comfort preference (1-10) |
| style_preferences | array | List of preferred styles |
| color_preferences | array | List of preferred colors |
| fit_preferences | array | List of preferred fits |

##### event_context Object

| Field | Type | Description |
|-------|------|-------------|
| event_type | string | Type of event (casual, formal, etc.) |
| formality_level | number | Formality level (1-5) |
| weather_conditions | array | List of weather conditions |
| time_of_day | string | Time of day (morning, afternoon, evening) |
| season | string | Season (spring, summer, fall, winter) |
| location | string | Location type (indoor, outdoor) |
| duration | number | Event duration in hours |
| activity_level | number | Activity level (1-5) |

#### Response

| Field | Type | Description |
|-------|------|-------------|
| outfit | object | Generated outfit details |

##### outfit Object

| Field | Type | Description |
|-------|------|-------------|
| style_preferences | array | Applied style preferences |
| color_preferences | array | Applied color preferences |
| materials | array | Selected materials |
| suitability | string | Outfit suitability rating |
| occasion | string | Target occasion |
| season | string | Target season |
| formality_level | number | Applied formality level |
| comfort_level | number | Applied comfort level |
| top | object | Top garment details |
| bottom | object | Bottom garment details |
| shoes | object | Shoe details |

#### Example Request

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

#### Example Response

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

#### Generate Individual Items

- `POST /api/generate/top` - Generate top only
- `POST /api/generate/bottom` - Generate bottom only
- `POST /api/generate/shoes` - Generate shoes only

#### Measurement Management

- `POST /api/measurements/validate` - Validate user measurements
- `POST /api/measurements/estimate` - Estimate missing measurements
- `GET /api/measurements/guide` - Get measurement guide
- `POST /api/measurements/body-type` - Determine body type

#### Material and Style Information

- `GET /api/materials` - Get available materials
- `GET /api/textures` - Get available textures
- `GET /api/material-combinations` - Get material combinations

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests:

- 200: Success
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

Error responses include a message describing the error:

```json
{
  "error": "Error message description"
}
```

## Rate Limiting

Currently, there are no rate limits implemented. Future versions may include rate limiting based on IP address or API key.

## Versioning

The API version is included in the URL path. The current version is v1.

## Support

For support, please open an issue in the GitHub repository or contact the development team. 