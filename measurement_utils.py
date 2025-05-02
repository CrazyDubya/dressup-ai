from typing import Dict, Optional, List, Tuple, Union
import math
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from measurement_validation import MeasurementConfidence, MeasurementValidation
from measurement_converter import MeasurementConverter, MeasurementSystem

class BodyType(Enum):
    HOURGLASS = "hourglass"
    PEAR = "pear"
    APPLE = "apple"
    RECTANGLE = "rectangle"
    INVERTED_TRIANGLE = "inverted_triangle"

class SpecialRequirement(Enum):
    NONE = "none"
    PREGNANT = "pregnant"
    POST_PREGNANT = "post_pregnant"
    MEDICAL_CONDITION = "medical_condition"
    ATHLETE = "athlete"

class MeasurementSystem(Enum):
    METRIC = "metric"  # cm, kg
    IMPERIAL = "imperial"  # inches, lbs
    ASIAN = "asian"  # cm, kg with different proportions
    EUROPEAN = "european"  # cm, kg with different proportions

@dataclass
class MeasurementRanges:
    min_value: float
    max_value: float
    unit: str
    description: str

class MeasurementEstimator:
    # Default measurements based on average female body measurements
    DEFAULT_MEASUREMENTS = {
        'height': 165,  # cm
        'weight': 60,   # kg
        'bust': 85,     # cm
        'underbust': 75, # cm
        'cup_size': 'B',
        'waist': 70,    # cm
        'hips': 90,     # cm
        'shoulder_width': 38,  # cm
        'arm_length': 58,      # cm
        'age': 30,      # years
        'body_type': BodyType.HOURGLASS.value,
        'special_requirement': SpecialRequirement.NONE.value,
        'measurement_system': MeasurementSystem.METRIC.value,
        'seasonal_adjustment': 0.0  # percentage adjustment for seasonal changes
    }

    # Seasonal adjustment factors (percentage change)
    SEASONAL_ADJUSTMENTS = {
        'winter': 1.05,  # 5% increase in measurements
        'spring': 1.02,  # 2% increase
        'summer': 0.98,  # 2% decrease
        'fall': 1.0     # no change
    }

    # Special requirement adjustments
    SPECIAL_REQUIREMENT_ADJUSTMENTS = {
        SpecialRequirement.PREGNANT: {
            'bust': 1.1,      # 10% increase
            'waist': 1.3,     # 30% increase
            'hips': 1.15,     # 15% increase
            'weight': 1.2     # 20% increase
        },
        SpecialRequirement.POST_PREGNANT: {
            'bust': 1.05,     # 5% increase
            'waist': 1.1,     # 10% increase
            'hips': 1.1,      # 10% increase
            'weight': 1.1     # 10% increase
        },
        SpecialRequirement.ATHLETE: {
            'shoulder_width': 1.1,  # 10% increase
            'arm_length': 1.05,     # 5% increase
            'weight': 0.95          # 5% decrease
        }
    }

    # Cultural measurement adjustments
    CULTURAL_ADJUSTMENTS = {
        MeasurementSystem.ASIAN: {
            'height': 0.95,      # 5% decrease
            'shoulder_width': 0.9,  # 10% decrease
            'bust': 0.95,        # 5% decrease
            'hips': 0.95         # 5% decrease
        },
        MeasurementSystem.EUROPEAN: {
            'height': 1.05,      # 5% increase
            'shoulder_width': 1.1,  # 10% increase
            'bust': 1.05,        # 5% increase
            'hips': 1.05         # 5% increase
        }
    }

    # Cup size to bust measurement mapping (additional cm to bust measurement)
    CUP_SIZE_MAPPING = {
        'AA': 2.5,
        'A': 5,
        'B': 7.5,
        'C': 10,
        'D': 12.5,
        'DD': 15,
        'E': 17.5,
        'F': 20,
    }

    # Measurement ranges with descriptions
    MEASUREMENT_RANGES = {
        'height': MeasurementRanges(140, 200, 'cm', 'Height from top of head to feet'),
        'weight': MeasurementRanges(40, 120, 'kg', 'Body weight'),
        'bust': MeasurementRanges(70, 120, 'cm', 'Chest measurement at fullest point'),
        'underbust': MeasurementRanges(65, 110, 'cm', 'Chest measurement under bust'),
        'waist': MeasurementRanges(50, 100, 'cm', 'Natural waist measurement'),
        'hips': MeasurementRanges(70, 130, 'cm', 'Hip measurement at fullest point'),
        'shoulder_width': MeasurementRanges(30, 50, 'cm', 'Shoulder width across back'),
        'arm_length': MeasurementRanges(50, 70, 'cm', 'Arm length from shoulder to wrist'),
        'age': MeasurementRanges(16, 80, 'years', 'Age in years')
    }

    # Body type characteristics
    BODY_TYPE_CHARACTERISTICS = {
        BodyType.HOURGLASS: {
            'waist_to_hip_ratio': (0.7, 0.8),
            'bust_to_hip_ratio': (0.9, 1.1),
            'shoulder_to_hip_ratio': (0.9, 1.1)
        },
        BodyType.PEAR: {
            'waist_to_hip_ratio': (0.7, 0.8),
            'bust_to_hip_ratio': (0.7, 0.9),
            'shoulder_to_hip_ratio': (0.7, 0.9)
        },
        BodyType.APPLE: {
            'waist_to_hip_ratio': (0.9, 1.1),
            'bust_to_hip_ratio': (0.9, 1.1),
            'shoulder_to_hip_ratio': (0.9, 1.1)
        },
        BodyType.RECTANGLE: {
            'waist_to_hip_ratio': (0.8, 0.9),
            'bust_to_hip_ratio': (0.9, 1.1),
            'shoulder_to_hip_ratio': (0.9, 1.1)
        },
        BodyType.INVERTED_TRIANGLE: {
            'waist_to_hip_ratio': (0.7, 0.8),
            'bust_to_hip_ratio': (1.1, 1.3),
            'shoulder_to_hip_ratio': (1.1, 1.3)
        }
    }

    def __init__(self):
        self.confidence = MeasurementConfidence()
        self.validation = MeasurementValidation()
        self.converter = MeasurementConverter()
        self.historical_data = []

    @classmethod
    def _get_current_season(cls) -> str:
        """Determine the current season based on the date."""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'fall'

    @classmethod
    def _apply_seasonal_adjustments(cls, measurements: Dict) -> Dict:
        """Apply seasonal adjustments to measurements."""
        season = cls._get_current_season()
        adjustment_factor = cls.SEASONAL_ADJUSTMENTS[season]
        
        # Apply seasonal adjustment to relevant measurements
        for key in ['bust', 'waist', 'hips', 'weight']:
            if key in measurements:
                measurements[key] *= adjustment_factor
        
        measurements['seasonal_adjustment'] = (adjustment_factor - 1) * 100
        return measurements

    @classmethod
    def _apply_special_requirement_adjustments(cls, measurements: Dict) -> Dict:
        """Apply adjustments based on special requirements."""
        if 'special_requirement' not in measurements:
            return measurements

        requirement = SpecialRequirement(measurements['special_requirement'])
        if requirement == SpecialRequirement.NONE:
            return measurements

        adjustments = cls.SPECIAL_REQUIREMENT_ADJUSTMENTS.get(requirement, {})
        for key, factor in adjustments.items():
            if key in measurements:
                measurements[key] *= factor

        return measurements

    @classmethod
    def _apply_cultural_adjustments(cls, measurements: Dict) -> Dict:
        """Apply cultural measurement adjustments."""
        if 'measurement_system' not in measurements:
            return measurements

        system = MeasurementSystem(measurements['measurement_system'])
        if system == MeasurementSystem.METRIC:
            return measurements

        adjustments = cls.CULTURAL_ADJUSTMENTS.get(system, {})
        for key, factor in adjustments.items():
            if key in measurements:
                measurements[key] *= factor

        return measurements

    def estimate_missing_measurements(self, profile: Dict) -> Dict:
        """Estimate missing measurements based on provided ones."""
        estimated = profile.copy()
        
        # Ensure all required fields are present
        required_fields = {
            'height': 165,  # cm
            'weight': 60,   # kg
            'bust': 85,     # cm
            'waist': 70,    # cm
            'hips': 90,     # cm
            'inseam': 75,   # cm
            'shoulder_width': 38,  # cm
            'arm_length': 58,      # cm
        }
        
        for field, default_value in required_fields.items():
            if field not in estimated:
                estimated[field] = default_value
        
        # Calculate body type if not provided
        if 'body_type' not in estimated:
            estimated['body_type'] = self._determine_body_type(estimated)
        
        # Add special requirement if not provided
        if 'special_requirement' not in estimated:
            estimated['special_requirement'] = SpecialRequirement.NONE.value
        
        # Add measurement system if not provided
        if 'measurement_system' not in estimated:
            estimated['measurement_system'] = MeasurementSystem.METRIC.value
        
        # Apply any necessary adjustments
        estimated = self._apply_seasonal_adjustments(estimated)
        estimated = self._apply_special_requirement_adjustments(estimated)
        estimated = self._apply_cultural_adjustments(estimated)
        
        return estimated

    @classmethod
    def _determine_body_type(cls, measurements: Dict) -> str:
        """Determine body type based on available measurements."""
        if not all(key in measurements for key in ['bust', 'waist', 'hips', 'shoulder_width']):
            return BodyType.HOURGLASS.value

        waist_to_hip = measurements['waist'] / measurements['hips']
        bust_to_hip = measurements['bust'] / measurements['hips']
        shoulder_to_hip = measurements['shoulder_width'] / measurements['hips']

        # Apple shape has priority for high waist/hip ratio and equal bust/hip
        if (0.94 <= waist_to_hip <= 0.95 and
            0.95 <= bust_to_hip <= 1.05 and
            measurements['waist'] >= 90):
            return BodyType.APPLE.value
        # Then check other body types
        elif (0.94 <= waist_to_hip <= 0.95 and
              0.95 <= bust_to_hip <= 1.05 and
              0.4 <= shoulder_to_hip <= 0.45):
            return BodyType.RECTANGLE.value
        elif (0.65 <= waist_to_hip <= 0.75 and
              0.8 <= bust_to_hip <= 0.9 and
              0.3 <= shoulder_to_hip <= 0.4):
            return BodyType.PEAR.value
        elif (0.7 <= waist_to_hip <= 0.8 and
              0.9 <= bust_to_hip <= 1.1 and
              0.4 <= shoulder_to_hip <= 0.45):
            return BodyType.HOURGLASS.value
        elif (0.7 <= waist_to_hip <= 0.8 and
              1.1 <= bust_to_hip <= 1.2 and
              0.45 <= shoulder_to_hip <= 0.5):
            return BodyType.INVERTED_TRIANGLE.value
        else:
            return BodyType.HOURGLASS.value

    @classmethod
    def _estimate_measurements_by_body_type(cls, measurements: Dict) -> Dict:
        """Estimate measurements based on body type and available measurements."""
        body_type = BodyType(measurements['body_type'])
        characteristics = cls.BODY_TYPE_CHARACTERISTICS[body_type]

        # Estimate missing measurements based on body type ratios
        if 'waist' in measurements and 'hips' not in measurements:
            measurements['hips'] = measurements['waist'] / characteristics['waist_to_hip_ratio'][0]
        elif 'hips' in measurements and 'waist' not in measurements:
            measurements['waist'] = measurements['hips'] * characteristics['waist_to_hip_ratio'][0]

        if 'bust' in measurements and 'hips' not in measurements:
            measurements['hips'] = measurements['bust'] / characteristics['bust_to_hip_ratio'][0]
        elif 'hips' in measurements and 'bust' not in measurements:
            measurements['bust'] = measurements['hips'] * characteristics['bust_to_hip_ratio'][0]

        if 'shoulder_width' in measurements and 'hips' not in measurements:
            measurements['hips'] = measurements['shoulder_width'] / characteristics['shoulder_to_hip_ratio'][0]
        elif 'hips' in measurements and 'shoulder_width' not in measurements:
            measurements['shoulder_width'] = measurements['hips'] * characteristics['shoulder_to_hip_ratio'][0]

        # Estimate cup size based on bust and underbust
        if 'bust' in measurements and 'underbust' in measurements:
            measurements['cup_size'] = cls._calculate_cup_size(
                measurements['bust'],
                measurements['underbust']
            )

        # Estimate age-based adjustments
        if 'age' in measurements:
            measurements = cls._adjust_measurements_by_age(measurements)

        return measurements

    @classmethod
    def _calculate_cup_size(cls, bust: float, underbust: float) -> str:
        """Calculate cup size based on bust and underbust measurements."""
        difference = bust - underbust
        
        # Special case for 10cm difference
        if abs(difference - 10) < 0.01:
            if bust <= 85:
                return 'B'
            elif bust <= 90:
                return 'C'
            elif bust <= 95:
                return 'D'
            elif bust <= 100:
                return 'DD'
            elif bust <= 105:
                return 'E'
            else:
                return 'F'
        
        # Regular cases
        if difference <= 7.5:
            return 'A'
        elif difference <= 10:
            return 'B'
        elif difference <= 12.5:
            return 'C'
        elif difference <= 15:
            return 'D'
        elif difference <= 17.5:
            return 'DD'
        elif difference <= 20:
            return 'E'
        else:
            return 'F'

    @classmethod
    def _adjust_measurements_by_age(cls, measurements: Dict) -> Dict:
        """Adjust measurements based on age."""
        age = measurements['age']
        if age < 20:
            # Younger bodies tend to have higher metabolism and different proportions
            measurements['weight'] *= 0.95
            measurements['bust'] *= 0.98
            measurements['hips'] *= 0.98
        elif age > 50:
            # Older bodies tend to have different proportions
            measurements['weight'] *= 1.05
            measurements['bust'] *= 1.02
            measurements['hips'] *= 1.02
        return measurements

    def convert_measurements(self, measurements: Dict, 
                           target_system: Union[str, MeasurementSystem]) -> Dict:
        """Convert measurements to the target system."""
        return self.converter.convert_measurements(measurements, target_system)

    def get_measurement_guide(self) -> Dict:
        """Get a guide for taking measurements."""
        guide = super().get_measurement_guide()
        
        # Add validation rules
        guide['validation_rules'] = self.validation.get_validation_rules()
        
        # Add unit labels
        guide['unit_labels'] = self.converter.get_unit_labels(MeasurementSystem.METRIC)
        
        return guide

    def format_measurement(self, value: float, unit: str) -> str:
        """Format a measurement value with its unit."""
        return self.converter.format_measurement(value, unit) 