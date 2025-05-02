# DressUp Measurement System

A comprehensive measurement system for fashion and clothing applications, providing accurate body measurements with support for different measurement systems, cultural adjustments, and special requirements.

## Features

### Core Measurement System
- Accurate body measurements calculation
- Support for multiple measurement systems (Metric, Imperial, Asian, European)
- Body type detection and analysis
- Cup size calculation
- Age-based measurement adjustments
- Seasonal measurement adjustments
- Machine learning-based measurement predictions (via measurement_ml.py)

### Measurement Validation
- Comprehensive validation rules for all measurements
- Relationship validation between measurements
- Range validation for each measurement type
- Detailed error reporting
- API endpoints for validation (measurement_endpoints.py)

### Measurement Confidence
- Confidence scoring for each measurement
- Historical data tracking
- Consistency checking
- Recency-based scoring
- Completeness validation

### Special Requirements Support
- Pregnancy adjustments
- Post-pregnancy adjustments
- Athletic body type adjustments
- Medical condition considerations

### Cultural Adjustments
- Asian body type adjustments
- European body type adjustments
- Customizable adjustment factors

### Additional Features
- REST API endpoints for measurement operations
- Web application interface
- User profile management
- Outfit catalog integration
- Style and material specifications
- Admin interface for monitoring
- Image generation and management
- Technical and style context management

## Installation

### Basic Installation
```bash
pip install -r requirements.txt
```

### API Installation
```bash
pip install -r api_requirements.txt
```

### Development Installation
```bash
pip install -e .
```

## Usage

### Basic Usage

```python
from measurement_utils import MeasurementEstimator

# Create an estimator instance
estimator = MeasurementEstimator()

# Estimate measurements with basic profile
measurements = {
    'height': 165,
    'weight': 60,
    'measurement_system': 'metric'
}
estimated = estimator.estimate_missing_measurements(measurements)
print(f"Estimated measurements: {estimated}")
```

### Converting Measurements

```python
# Convert to imperial units
imperial = estimator.convert_measurements(estimated, 'imperial')
print(f"Imperial measurements: {imperial}")

# Convert to Asian measurements
asian = estimator.convert_measurements(estimated, 'asian')
print(f"Asian measurements: {asian}")
```

### Special Requirements

```python
# Add special requirements
measurements = {
    'height': 165,
    'weight': 60,
    'special_requirement': 'pregnant'
}
estimated = estimator.estimate_missing_measurements(measurements)
```

### Getting Measurement Guide

```python
# Get measurement guide with validation rules
guide = estimator.get_measurement_guide()
print(f"Measurement guide: {guide}")
```

### API Usage
See `api_readme.md` for detailed API documentation and examples.

## Project Structure

```
dressup/
├── measurement_utils.py      # Core measurement utilities
├── measurement_validation.py # Measurement validation logic
├── measurement_converter.py  # Unit conversion utilities
├── measurement_ml.py        # ML-based measurement predictions
├── measurement_endpoints.py  # API endpoints
├── api.py                   # Main API implementation
├── user_interface.py        # Web interface
├── user_profile.py          # User profile management
├── style_context.py         # Style definitions
├── material_specs.py        # Material specifications
├── admin.py                 # Admin interface
├── web_app/                 # Web application files
├── docs/                    # Documentation
├── tests/                   # Test files
└── requirements.txt         # Dependencies
```

## Measurement Types

The system supports the following measurements:
- Height
- Weight
- Bust
- Underbust
- Cup Size
- Waist
- Hips
- Shoulder Width
- Arm Length

## Body Types

Supported body types:
- Hourglass
- Pear
- Apple
- Rectangle
- Inverted Triangle

## Measurement Systems

- Metric (cm, kg)
- Imperial (inches, lbs)
- Asian (with cultural adjustments)
- European (with cultural adjustments)

## Running the Application

### API Server
To start the API server:
```bash
python api.py
```
This will start the Flask server with endpoints for outfit generation and measurement management.

### Admin Interface
To access the admin interface:
```bash
python admin.py
```
This provides an interactive CLI for:
- Viewing A/B testing statistics
- Monitoring error logs
- Managing system settings

### Running Tests
To run the test suite:
```bash
pytest
```
This will execute all test files:
- test_api.py
- test_measurement_endpoints.py
- test_measurement_utils.py
- test_enhancements.py

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special thanks to the fashion industry experts who provided insights for the measurement calculations 