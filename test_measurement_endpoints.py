import pytest
from fastapi.testclient import TestClient
from measurement_utils import MeasurementEstimator, BodyType
import json

@pytest.fixture
def client():
    from api import app
    with TestClient(app) as client:
        yield client

@pytest.fixture
def valid_measurements():
    return {
        'height': 170,
        'weight': 65,
        'bust': 90,
        'underbust': 80,
        'cup_size': 'D',
        'waist': 70,
        'hips': 95,
        'shoulder_width': 40,
        'arm_length': 60,
        'age': 30,
        'body_type': 'hourglass'
    }

@pytest.fixture
def partial_measurements():
    return {
        'height': 170,
        'bust': 90,
        'waist': 70
    }

class TestMeasurementEndpoints:
    def test_validate_measurements_valid(self, client, valid_measurements):
        """Test validation endpoint with valid measurements."""
        response = client.post('/api/measurements/validate', json=valid_measurements)
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] is True
        assert 'message' in data

    def test_validate_measurements_invalid(self, client):
        """Test validation endpoint with invalid measurements."""
        invalid_measurements = {
            'height': 300,  # Too tall
            'weight': 200,  # Too heavy
            'cup_size': 'X',  # Invalid cup size
            'body_type': 'invalid'  # Invalid body type
        }
        response = client.post('/api/measurements/validate', json=invalid_measurements)
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] is False
        assert 'errors' in data
        assert len(data['errors']) == 4

    def test_validate_measurements_empty(self, client):
        """Test validation endpoint with empty measurements."""
        response = client.post('/api/measurements/validate', json={})
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] is False
        assert 'errors' in data
        assert "No measurements provided" in data['errors']

    def test_estimate_measurements_empty(self, client):
        """Test estimation endpoint with empty measurements."""
        response = client.post('/api/measurements/estimate', json={})
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
        assert "No measurements provided" in data['error']

    def test_estimate_measurements_partial(self, client, partial_measurements):
        """Test estimation endpoint with partial measurements."""
        response = client.post('/api/measurements/estimate', json=partial_measurements)
        assert response.status_code == 200
        data = response.json()
        assert 'measurements' in data
        assert 'body_type' in data
        
        # Check that provided measurements are not estimated
        for key in partial_measurements:
            assert not data['measurements'][key]['was_estimated']
            assert data['measurements'][key]['value'] == partial_measurements[key]
        
        # Check that all required measurements are present
        assert all(key in data['measurements'] for key in MeasurementEstimator.DEFAULT_MEASUREMENTS)

    def test_get_measurement_guide(self, client):
        """Test measurement guide endpoint."""
        response = client.get('/api/measurements/guide')
        assert response.status_code == 200
        data = response.json()
        assert 'guide' in data
        assert 'default_measurements' in data
        assert 'valid_ranges' in data
        
        # Check guide structure
        guide = data['guide']
        assert 'height' in guide
        assert 'bust' in guide
        assert 'underbust' in guide
        assert 'waist' in guide
        assert 'hips' in guide
        assert 'shoulder_width' in guide
        assert 'arm_length' in guide
        
        # Check each measurement guide entry
        for key in guide:
            assert 'description' in guide[key]
            assert 'tips' in guide[key]
            assert isinstance(guide[key]['tips'], list)

    def test_determine_body_type(self, client, valid_measurements):
        """Test body type determination endpoint."""
        response = client.post('/api/measurements/body-type', json=valid_measurements)
        assert response.status_code == 200
        data = response.json()
        assert 'body_type' in data
        assert 'characteristics' in data
        assert 'measurements' in data
        
        # Check body type characteristics
        characteristics = data['characteristics']
        assert 'waist_to_hip_ratio' in characteristics
        assert 'bust_to_hip_ratio' in characteristics
        assert 'shoulder_to_hip_ratio' in characteristics
        
        # Check measurements
        assert all(key in data['measurements'] for key in MeasurementEstimator.DEFAULT_MEASUREMENTS)

    def test_determine_body_type_partial(self, client, partial_measurements):
        """Test body type determination with partial measurements."""
        response = client.post('/api/measurements/body-type', json=partial_measurements)
        assert response.status_code == 200
        data = response.json()
        assert 'body_type' in data
        assert 'characteristics' in data
        assert 'measurements' in data
        
        # Check that all measurements are present
        assert all(key in data['measurements'] for key in MeasurementEstimator.DEFAULT_MEASUREMENTS)

    def test_determine_body_type_invalid(self, client):
        """Test body type determination with invalid measurements."""
        invalid_measurements = {
            'height': 300,  # Too tall
            'weight': 200,  # Too heavy
            'cup_size': 'X',  # Invalid cup size
            'body_type': 'invalid'  # Invalid body type
        }
        response = client.post('/api/measurements/body-type', json=invalid_measurements)
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data 
