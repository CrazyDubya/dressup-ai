import pytest
from measurement_utils import MeasurementEstimator, BodyType, MeasurementRanges

class TestMeasurementEstimator:
    def test_default_measurements(self):
        """Test that default measurements are within valid ranges."""
        for key, value in MeasurementEstimator.DEFAULT_MEASUREMENTS.items():
            if key in MeasurementEstimator.MEASUREMENT_RANGES:
                range_info = MeasurementEstimator.MEASUREMENT_RANGES[key]
                assert range_info.min_value <= value <= range_info.max_value

    def test_validate_measurements_empty(self):
        """Test validation with empty measurements."""
        is_valid, errors = MeasurementEstimator.validate_measurements({})
        assert not is_valid
        assert "No measurements provided" in errors

    def test_validate_measurements_valid(self):
        """Test validation with valid measurements."""
        measurements = {
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
        is_valid, errors = MeasurementEstimator.validate_measurements(measurements)
        assert is_valid
        assert not errors

    def test_validate_measurements_invalid(self):
        """Test validation with invalid measurements."""
        measurements = {
            'height': 300,  # Too tall
            'weight': 200,  # Too heavy
            'cup_size': 'X',  # Invalid cup size
            'body_type': 'invalid'  # Invalid body type
        }
        is_valid, errors = MeasurementEstimator.validate_measurements(measurements)
        assert not is_valid
        assert len(errors) == 4

    def test_estimate_missing_measurements_empty(self):
        """Test estimation with empty measurements."""
        estimated = MeasurementEstimator.estimate_missing_measurements({})
        assert all(key in estimated for key in MeasurementEstimator.DEFAULT_MEASUREMENTS)
        assert all(estimated[key] == MeasurementEstimator.DEFAULT_MEASUREMENTS[key] 
                  for key in MeasurementEstimator.DEFAULT_MEASUREMENTS)

    def test_estimate_missing_measurements_partial(self):
        """Test estimation with partial measurements."""
        partial = {
            'height': 170,
            'bust': 90,
            'waist': 70
        }
        estimated = MeasurementEstimator.estimate_missing_measurements(partial)
        assert estimated['height'] == 170
        assert estimated['bust'] == 90
        assert estimated['waist'] == 70
        assert all(key in estimated for key in MeasurementEstimator.DEFAULT_MEASUREMENTS)

    def test_calculate_cup_size(self):
        """Test cup size calculation."""
        test_cases = [
            (85, 75, 'B'),  # 10cm difference
            (90, 80, 'C'),  # 10cm difference
            (95, 85, 'D'),  # 10cm difference
            (100, 90, 'DD'),  # 10cm difference
            (105, 95, 'E'),  # 10cm difference
            (110, 100, 'F'),  # 10cm difference
        ]
        for bust, underbust, expected in test_cases:
            assert MeasurementEstimator._calculate_cup_size(bust, underbust) == expected

    def test_determine_body_type(self):
        """Test body type determination."""
        test_cases = [
            # Hourglass
            {
                'bust': 90,
                'waist': 70,
                'hips': 95,
                'shoulder_width': 40,
                'expected': 'hourglass'
            },
            # Pear
            {
                'bust': 85,
                'waist': 70,
                'hips': 100,
                'shoulder_width': 35,
                'expected': 'pear'
            },
            # Apple
            {
                'bust': 95,
                'waist': 90,
                'hips': 95,
                'shoulder_width': 40,
                'expected': 'apple'
            },
            # Rectangle
            {
                'bust': 90,
                'waist': 85,
                'hips': 90,
                'shoulder_width': 40,
                'expected': 'rectangle'
            },
            # Inverted Triangle
            {
                'bust': 100,
                'waist': 70,
                'hips': 90,
                'shoulder_width': 45,
                'expected': 'inverted_triangle'
            }
        ]
        for case in test_cases:
            body_type = MeasurementEstimator._determine_body_type(case)
            assert body_type == case['expected']

    def test_adjust_measurements_by_age(self):
        """Test age-based measurement adjustments."""
        measurements = {
            'weight': 60,
            'bust': 85,
            'hips': 90,
            'age': 30
        }
        
        # Test young age adjustment
        young = measurements.copy()
        young['age'] = 18
        adjusted = MeasurementEstimator._adjust_measurements_by_age(young)
        assert adjusted['weight'] == 57  # 60 * 0.95
        assert adjusted['bust'] == 83.3  # 85 * 0.98
        assert adjusted['hips'] == 88.2  # 90 * 0.98

        # Test older age adjustment
        old = measurements.copy()
        old['age'] = 55
        adjusted = MeasurementEstimator._adjust_measurements_by_age(old)
        assert adjusted['weight'] == 63  # 60 * 1.05
        assert adjusted['bust'] == 86.7  # 85 * 1.02
        assert adjusted['hips'] == 91.8  # 90 * 1.02

    def test_get_measurement_guide(self):
        """Test measurement guide generation."""
        guide = MeasurementEstimator.get_measurement_guide()
        assert 'height' in guide
        assert 'bust' in guide
        assert 'underbust' in guide
        assert 'waist' in guide
        assert 'hips' in guide
        assert 'shoulder_width' in guide
        assert 'arm_length' in guide
        
        # Check guide structure
        for key in guide:
            assert 'description' in guide[key]
            assert 'tips' in guide[key]
            assert isinstance(guide[key]['tips'], list) 
