# DressUp API Documentation

The DressUp API is a RESTful service that generates personalized outfit recommendations based on user profiles and event contexts. This API helps users find the perfect outfit for any occasion by considering their measurements, preferences, and the specific requirements of the event.

## Base URL

```
http://localhost:5000
```

## Authentication

Currently, the API does not require authentication.

## Measurement System

The API includes a comprehensive measurement system that helps users get accurate measurements and estimates missing ones.

### Measurement Endpoints

#### 1. Validate Measurements

Validate user measurements and get detailed feedback.

```http
POST /api/measurements/validate
```

##### Request Body

```json
{
    "height": 170,
    "weight": 65,
    "bust": 90,
    "underbust": 80,
    "cup_size": "D",
    "waist": 70,
    "hips": 95,
    "shoulder_width": 40,
    "arm_length": 60,
    "age": 30,
    "body_type": "hourglass"
}
```

##### Response

```json
{
    "valid": true,
    "message": "All measurements are valid"
}
```

Or if there are errors:

```json
{
    "valid": false,
    "errors": [
        "height (180 cm) is outside valid range (140-200 cm)",
        "Invalid cup size: X"
    ]
}
```

#### 2. Estimate Measurements

Estimate missing measurements based on provided ones.

```http
POST /api/measurements/estimate
```

##### Request Body

```json
{
    "height": 170,
    "bust": 90,
    "waist": 70
}
```

##### Response

```json
{
    "measurements": {
        "height": {
            "value": 170,
            "was_estimated": false
        },
        "weight": {
            "value": 65.5,
            "was_estimated": true
        },
        "bust": {
            "value": 90,
            "was_estimated": false
        },
        "underbust": {
            "value": 80,
            "was_estimated": true
        },
        "cup_size": {
            "value": "D",
            "was_estimated": true
        },
        "waist": {
            "value": 70,
            "was_estimated": false
        },
        "hips": {
            "value": 91,
            "was_estimated": true
        },
        "shoulder_width": {
            "value": 39.1,
            "was_estimated": true
        },
        "arm_length": {
            "value": 59.5,
            "was_estimated": true
        },
        "age": {
            "value": 30,
            "was_estimated": true
        },
        "body_type": {
            "value": "hourglass",
            "was_estimated": true
        }
    },
    "body_type": "hourglass"
}
```

#### 3. Get Measurement Guide

Get a guide for taking measurements.

```http
GET /api/measurements/guide
```

##### Response

```json
{
    "guide": {
        "height": {
            "description": "Stand straight against a wall, measure from top of head to feet",
            "tips": ["Stand straight", "Look forward", "Keep heels together"]
        },
        "bust": {
            "description": "Measure around the fullest part of your bust",
            "tips": ["Wear a non-padded bra", "Keep tape measure parallel to floor"]
        },
        "underbust": {
            "description": "Measure directly under your bust",
            "tips": ["Keep tape measure snug", "Breathe normally"]
        },
        "waist": {
            "description": "Measure at your natural waist (smallest part)",
            "tips": ["Stand straight", "Don't suck in your stomach"]
        },
        "hips": {
            "description": "Measure around the fullest part of your hips",
            "tips": ["Stand with feet together", "Keep tape measure parallel to floor"]
        },
        "shoulder_width": {
            "description": "Measure across your back from shoulder to shoulder",
            "tips": ["Stand straight", "Keep arms relaxed"]
        },
        "arm_length": {
            "description": "Measure from shoulder to wrist",
            "tips": ["Keep arm slightly bent", "Measure along the outside of arm"]
        }
    },
    "default_measurements": {
        "height": 165,
        "weight": 60,
        "bust": 85,
        "underbust": 75,
        "cup_size": "B",
        "waist": 70,
        "hips": 90,
        "shoulder_width": 38,
        "arm_length": 58,
        "age": 30,
        "body_type": "hourglass"
    },
    "valid_ranges": {
        "height": {
            "min": 140,
            "max": 200,
            "unit": "cm",
            "description": "Height from top of head to feet"
        },
        "weight": {
            "min": 40,
            "max": 120,
            "unit": "kg",
            "description": "Body weight"
        },
        "bust": {
            "min": 70,
            "max": 120,
            "unit": "cm",
            "description": "Chest measurement at fullest point"
        },
        "underbust": {
            "min": 65,
            "max": 110,
            "unit": "cm",
            "description": "Chest measurement under bust"
        },
        "waist": {
            "min": 50,
            "max": 100,
            "unit": "cm",
            "description": "Natural waist measurement"
        },
        "hips": {
            "min": 70,
            "max": 130,
            "unit": "cm",
            "description": "Hip measurement at fullest point"
        },
        "shoulder_width": {
            "min": 30,
            "max": 50,
            "unit": "cm",
            "description": "Shoulder width across back"
        },
        "arm_length": {
            "min": 50,
            "max": 70,
            "unit": "cm",
            "description": "Arm length from shoulder to wrist"
        },
        "age": {
            "min": 16,
            "max": 80,
            "unit": "years",
            "description": "Age in years"
        }
    }
}
```

#### 4. Determine Body Type

Determine body type based on provided measurements.

```http
POST /api/measurements/body-type
```

##### Request Body

```json
{
    "height": 170,
    "weight": 65,
    "bust": 90,
    "waist": 70,
    "hips": 95,
    "shoulder_width": 40
}
```

##### Response

```json
{
    "body_type": "hourglass",
    "characteristics": {
        "waist_to_hip_ratio": [0.7, 0.8],
        "bust_to_hip_ratio": [0.9, 1.1],
        "shoulder_to_hip_ratio": [0.9, 1.1]
    },
    "measurements": {
        "height": 170,
        "weight": 65,
        "bust": 90,
        "underbust": 80,
        "cup_size": "D",
        "waist": 70,
        "hips": 95,
        "shoulder_width": 40,
        "arm_length": 59.5,
        "age": 30,
        "body_type": "hourglass"
    }
}
```

### Body Types

The API supports the following body types:

- **Hourglass**: Balanced proportions with defined waist
- **Pear**: Wider hips than shoulders
- **Apple**: Wider waist than hips
- **Rectangle**: Similar measurements throughout
- **Inverted Triangle**: Wider shoulders than hips

### Measurement Estimation Rules

- Height and Weight: Estimated using BMI formula (target BMI of 21)
- Bust and Cup Size: Estimated based on bust and underbust measurements
- Waist and Hips: Estimated using body type-specific ratios
- Shoulder Width: Estimated based on body type and available measurements
- Arm Length: Estimated as percentage of height
- Age-based adjustments for different age groups

## Endpoints

### 1. Generate Top

Generate a top (shirt, blouse, etc.) based on user profile and event context.

```http
POST /api/generate/top
```

#### Request Body

```json
{
    "user_profile": {
        "height": 170,
        "weight": 65,
        "bust": 90,
        "cup_size": "D",
        "waist": 70,
        "hips": 95,
        "shoulder_width": 40,
        "arm_length": 60,
        "username": "user123"
    },
    "event": {
        "type": "wedding",
        "formality": 8,
        "season": "spring",
        "location": "outdoor"
    }
}
```

Note: All user_profile fields are optional. Missing measurements will be estimated.

#### Response

```json
{
    "top": {
        "description": "White silk blouse",
        "material": "silk",
        "color": "white",
        "fit": "regular",
        "features": ["ruffled collar", "long sleeves"],
        "suitable_for": ["wedding"],
        "bust_fit": "comfortable",
        "shoulder_fit": "perfect",
        "arm_fit": "relaxed"
    }
}
```

### 2. Generate Bottom

Generate a bottom (pants, skirt, etc.) based on user profile and event context.

```http
POST /api/generate/bottom
```

#### Request Body

Same as Generate Top endpoint.

#### Response

```json
{
    "bottom": {
        "description": "Black pencil skirt",
        "material": "wool blend",
        "color": "black",
        "fit": "slim",
        "features": ["knee length", "back slit"],
        "suitable_for": ["wedding"],
        "waist_fit": "fitted",
        "hip_fit": "comfortable",
        "length": "knee"
    }
}
```

### 3. Generate Shoes

Generate shoes based on user profile and event context.

```http
POST /api/generate/shoes
```

#### Request Body

```json
{
    "user_profile": {
        "height": 170,
        "weight": 65,
        "bust": 90,
        "cup_size": "D",
        "waist": 70,
        "hips": 95,
        "shoulder_width": 40,
        "arm_length": 60,
        "username": "user123",
        "shoe_size": 39,
        "heel_height_preference": 7,
        "heel_width_preference": "medium",
        "open_toe_preference": true,
        "comfort_priority": 8
    },
    "event": {
        "type": "wedding",
        "formality": 8,
        "season": "spring",
        "location": "outdoor"
    }
}
```

#### Response

```json
{
    "shoes": {
        "description": "Black leather pumps",
        "material": "leather",
        "color": "black",
        "heel_height": 3,
        "heel_width": "medium",
        "open_toe": false,
        "comfort_level": 7,
        "arch_support": "medium",
        "sole_type": "leather",
        "closure_type": "slip-on"
    }
}
```

### 4. Generate Accessories

Generate accessories based on user profile and event context.

```http
POST /api/generate/accessories
```

#### Request Body

Same as Generate Top endpoint.

#### Response

```json
{
    "accessories": [
        {
            "type": "necklace",
            "description": "Pearl necklace",
            "material": "pearl",
            "color": "white",
            "features": ["single strand"],
            "placement": "neck",
            "size": "medium",
            "style": "classic"
        }
    ]
}
```

### 5. Generate Complete Outfit

Generate a complete outfit including all components.

```http
POST /api/generate/complete-outfit
```

#### Request Body

Same as Generate Top endpoint.

#### Response

```json
{
    "outfit": {
        "top": { ... },
        "bottom": { ... },
        "shoes": { ... },
        "accessories": [ ... ],
        "style": {"formal": 8, "classic": 7, "elegant": 9},
        "colors": ["white", "black"],
        "materials": ["silk", "wool", "leather", "pearl"],
        "suitable_for": ["wedding"],
        "occasion": "wedding",
        "season": "spring",
        "formality_level": 8,
        "comfort_level": 8
    }
}
```

### 6. Generate Event-Specific Outfit

Generate an outfit specific to an event type.

```http
POST /api/generate/event-specific/{event_type}
```

#### URL Parameters

- `event_type`: One of the following values:
  - wedding
  - business
  - casual
  - formal
  - party
  - date
  - travel
  - sports
  - beach
  - winter

#### Request Body

```json
{
    "user_profile": {
        "height": 170,
        "weight": 65,
        "bust": 90,
        "cup_size": "D",
        "waist": 70,
        "hips": 95,
        "shoulder_width": 40,
        "arm_length": 60,
        "username": "user123"
    },
    "formality": 8,
    "season": "spring",
    "location": "outdoor"
}
```

#### Response

Same as Generate Complete Outfit endpoint, with additional `event_specific_notes` field.

## Data Validation

### User Profile Requirements

- All measurements must be numeric values
- Required fields:
  - height
  - weight
  - bust
  - cup_size (string)
  - waist
  - hips
  - shoulder_width
  - arm_length

### Event Context Requirements

- Required fields:
  - type (must be one of the valid event types)
  - formality (1-10)
  - season (spring, summer, fall, winter)
  - location (indoor, outdoor, mixed)

### Shoe Preferences Requirements

- Required fields:
  - shoe_size (numeric)
  - heel_height_preference (numeric)
  - heel_width_preference (narrow, medium, wide)
  - open_toe_preference (boolean)
  - comfort_priority (numeric)

## Error Handling

The API returns appropriate HTTP status codes:

- 200: Success
- 400: Bad Request (invalid input data)
- 500: Internal Server Error

Error responses include a message explaining the issue:

```json
{
    "error": "Invalid user profile data"
}
```

## Example Usage

### Python

```python
import requests
import json

base_url = "http://localhost:5000"

# User profile data
user_profile = {
    "height": 170,
    "weight": 65,
    "bust": 90,
    "cup_size": "D",
    "waist": 70,
    "hips": 95,
    "shoulder_width": 40,
    "arm_length": 60,
    "username": "user123"
}

# Event context
event_context = {
    "type": "wedding",
    "formality": 8,
    "season": "spring",
    "location": "outdoor"
}

# Generate complete outfit
response = requests.post(
    f"{base_url}/api/generate/complete-outfit",
    json={
        "user_profile": user_profile,
        "event": event_context
    }
)

if response.status_code == 200:
    outfit = response.json()
    print(json.dumps(outfit, indent=2))
else:
    print(f"Error: {response.json()['error']}")
```

### cURL

```bash
curl -X POST http://localhost:5000/api/generate/complete-outfit \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "height": 170,
      "weight": 65,
      "bust": 90,
      "cup_size": "D",
      "waist": 70,
      "hips": 95,
      "shoulder_width": 40,
      "arm_length": 60,
      "username": "user123"
    },
    "event": {
      "type": "wedding",
      "formality": 8,
      "season": "spring",
      "location": "outdoor"
    }
  }'
```

## Rate Limiting

Currently, there are no rate limits implemented.

## Support

For support or to report issues, please contact the development team. 