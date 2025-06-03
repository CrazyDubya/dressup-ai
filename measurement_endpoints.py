from flask import Blueprint, jsonify, request
from measurement_utils import MeasurementEstimator, BodyType
from measurement_validation import MeasurementValidation

measurement_bp = Blueprint('measurement_bp', __name__)

estimator = MeasurementEstimator()
validator = MeasurementValidation()

@measurement_bp.route('/api/measurements/validate', methods=['POST'])
def validate_measurements_endpoint():
    data = request.get_json() or {}
    if not data:
        return jsonify(valid=False, errors=["No measurements provided"]), 400
    valid, errors = validator.validate_measurements(data)
    if valid:
        return jsonify(valid=True, message="All measurements are valid")
    return jsonify(valid=False, errors=errors), 400

@measurement_bp.route('/api/measurements/estimate', methods=['POST'])
def estimate_measurements_endpoint():
    data = request.get_json() or {}
    if not data:
        return jsonify(error="No measurements provided"), 400
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
    return jsonify(response)

@measurement_bp.route('/api/measurements/guide', methods=['GET'])
def get_measurement_guide():
    guide = validator.get_validation_rules()
    return jsonify({
        'guide': {k: {'description': v, 'tips': []} for k, v in guide.items()},
        'default_measurements': MeasurementEstimator.DEFAULT_MEASUREMENTS,
        'valid_ranges': validator.normal_ranges,
    })

@measurement_bp.route('/api/measurements/body-type', methods=['POST'])
def determine_body_type_endpoint():
    data = request.get_json() or {}
    if not data:
        return jsonify(error="No measurements provided"), 400
    measurements = estimator.estimate_missing_measurements(data)
    body_type = estimator._determine_body_type(measurements)
    characteristics = MeasurementEstimator.BODY_TYPE_CHARACTERISTICS[BodyType(body_type)]
    return jsonify({
        'body_type': body_type,
        'characteristics': characteristics,
        'measurements': measurements,
    })

