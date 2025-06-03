"""Measurement related API endpoints."""

from typing import Dict, Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from measurement_utils import MeasurementEstimator, BodyType
from measurement_validation import MeasurementValidation

measurement_router = APIRouter()

estimator = MeasurementEstimator()
validator = MeasurementValidation()

@measurement_router.post('/api/measurements/validate')
async def validate_measurements_endpoint(data: Dict[str, Any]):
    if not data:
        return JSONResponse(status_code=200, content={"valid": False, "errors": ["No measurements provided"]})
    valid, errors = validator.validate_measurements(data)
    if valid:
        return {"valid": True, "message": "All measurements are valid"}
    return {"valid": False, "errors": errors}

@measurement_router.post('/api/measurements/estimate')
async def estimate_measurements_endpoint(data: Dict[str, Any]):
    if not data:
        return JSONResponse(status_code=400, content={"error": "No measurements provided"})
    estimated = estimator.estimate_missing_measurements(data)
    response = {
        'measurements': {
            k: {
                'value': v,
                'was_estimated': k not in data
            } for k, v in estimated.items()
        },
        'body_type': estimated.get('body_type')
    }
    return response

@measurement_router.get('/api/measurements/guide')
async def get_measurement_guide():
    guide = validator.get_validation_rules()
    return {
        'guide': {k: {'description': v, 'tips': []} for k, v in guide.items()},
        'default_measurements': MeasurementEstimator.DEFAULT_MEASUREMENTS,
        'valid_ranges': estimator.confidence.normal_ranges,
    }

@measurement_router.post('/api/measurements/body-type')
async def determine_body_type_endpoint(data: Dict[str, Any]):
    if not data:
        return JSONResponse(status_code=400, content={"error": "No measurements provided"})
    valid, errors = validator.validate_measurements(data)
    if not valid:
        return JSONResponse(status_code=400, content={"error": "Invalid measurements", "errors": errors})
    measurements = estimator.estimate_missing_measurements(data)
    body_type = estimator._determine_body_type(measurements)
    characteristics = MeasurementEstimator.BODY_TYPE_CHARACTERISTICS[BodyType(body_type)]
    return {
        'body_type': body_type,
        'characteristics': characteristics,
        'measurements': measurements,
    }

