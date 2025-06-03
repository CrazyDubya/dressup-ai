from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from enum import Enum
import math

class MeasurementConfidence:
    def __init__(self):
        # Define confidence factors and their weights
        self.confidence_factors = {
            'recency': 0.3,        # How recent the measurement is
            'consistency': 0.3,     # How consistent with historical data
            'range_validity': 0.2,  # Whether within normal ranges
            'completeness': 0.2     # How many measurements are available
        }
        
        # Define normal ranges for measurements (in cm)
        self.normal_ranges = {
            'height': (140, 200),
            'weight': (40, 120),
            'bust': (70, 120),
            'underbust': (65, 110),
            'waist': (50, 100),
            'hips': (70, 130),
            'shoulder_width': (30, 50),
            'arm_length': (50, 70)
        }
        
        # Define measurement dependencies
        self.measurement_dependencies = {
            'bust': ['underbust'],
            'waist': ['hips'],
            'shoulder_width': ['height']
        }

    def calculate_confidence(self, measurements: Dict, 
                           historical_data: Optional[List[Dict]] = None,
                           measurement_date: Optional[datetime] = None) -> Dict[str, float]:
        """Calculate confidence scores for each measurement."""
        confidence_scores = {}
        
        for key, value in measurements.items():
            if key in self.normal_ranges:
                # Calculate individual factor scores
                recency_score = self._calculate_recency_score(measurement_date)
                consistency_score = self._calculate_consistency_score(key, value, historical_data)
                range_score = self._calculate_range_score(key, value)
                completeness_score = self._calculate_completeness_score(measurements)
                
                # Calculate weighted average
                confidence_scores[key] = (
                    recency_score * self.confidence_factors['recency'] +
                    consistency_score * self.confidence_factors['consistency'] +
                    range_score * self.confidence_factors['range_validity'] +
                    completeness_score * self.confidence_factors['completeness']
                )
        
        return confidence_scores

    def _calculate_recency_score(self, measurement_date: Optional[datetime]) -> float:
        """Calculate score based on how recent the measurement is."""
        if not measurement_date:
            return 0.5  # Default score if no date provided
        
        days_old = (datetime.now() - measurement_date).days
        if days_old <= 7:
            return 1.0
        elif days_old <= 30:
            return 0.8
        elif days_old <= 90:
            return 0.6
        elif days_old <= 180:
            return 0.4
        else:
            return 0.2

    def _calculate_consistency_score(self, key: str, value: float, 
                                   historical_data: Optional[List[Dict]]) -> float:
        """Calculate score based on consistency with historical data."""
        if not historical_data:
            return 0.5  # Default score if no historical data
        
        values = [data.get(key, value) for data in historical_data if key in data]
        if not values:
            return 0.5
        
        mean = sum(values) / len(values)
        std_dev = math.sqrt(sum((x - mean) ** 2 for x in values) / len(values))
        
        if std_dev == 0:
            return 1.0 if abs(value - mean) < 0.1 else 0.0
        
        z_score = abs(value - mean) / std_dev
        if z_score <= 1:
            return 1.0
        elif z_score <= 2:
            return 0.8
        elif z_score <= 3:
            return 0.6
        else:
            return 0.4

    def _calculate_range_score(self, key: str, value: float) -> float:
        """Calculate score based on whether the value is within normal range."""
        if key not in self.normal_ranges:
            return 0.5
        
        min_val, max_val = self.normal_ranges[key]
        if min_val <= value <= max_val:
            return 1.0
        elif min_val * 0.9 <= value <= max_val * 1.1:
            return 0.8
        elif min_val * 0.8 <= value <= max_val * 1.2:
            return 0.6
        else:
            return 0.4

    def _calculate_completeness_score(self, measurements: Dict) -> float:
        """Calculate score based on how many measurements are available."""
        required_measurements = set(self.normal_ranges.keys())
        available_measurements = set(measurements.keys())
        
        # Check dependencies
        for key, deps in self.measurement_dependencies.items():
            if key in available_measurements:
                for dep in deps:
                    if dep not in available_measurements:
                        available_measurements.remove(key)
                        break
        
        return len(available_measurements) / len(required_measurements)

class MeasurementValidation:
    def __init__(self):
        # Define validation rules for each measurement
        self.validation_rules = {
            'height': lambda x: 140 <= x <= 200,
            'weight': lambda x: 40 <= x <= 120,
            'bust': lambda x: 70 <= x <= 120,
            'underbust': lambda x: 65 <= x <= 110,
            'waist': lambda x: 50 <= x <= 100,
            'hips': lambda x: 70 <= x <= 130,
            'shoulder_width': lambda x: 30 <= x <= 50,
            'arm_length': lambda x: 50 <= x <= 70
        }
        
        # Define relationship rules between measurements
        self.relationship_rules = [
            lambda m: m['bust'] > m['underbust'],
            lambda m: m['hips'] > m['waist'],
            lambda m: m['height'] > m['arm_length'],
            lambda m: m['shoulder_width'] < m['height'] * 0.3
        ]

    def validate_measurements(self, measurements: Dict) -> Tuple[bool, List[str]]:
        """Validate measurements against rules and relationships."""
        errors = []
        
        # Check individual measurement rules
        for key, value in measurements.items():
            if key in self.validation_rules:
                if not self.validation_rules[key](value):
                    errors.append(f"Invalid {key} value: {value}")
        
        # Check relationship rules
        for rule in self.relationship_rules:
            try:
                if not rule(measurements):
                    errors.append("Invalid relationship between measurements")
            except KeyError:
                continue
        
        return len(errors) == 0, errors

    def get_validation_rules(self) -> Dict[str, str]:
        """Get human-readable descriptions of validation rules."""
        return {
            'height': "Height must be between 140cm and 200cm",
            'weight': "Weight must be between 40kg and 120kg",
            'bust': "Bust must be between 70cm and 120cm",
            'underbust': "Underbust must be between 65cm and 110cm",
            'waist': "Waist must be between 50cm and 100cm",
            'hips': "Hips must be between 70cm and 130cm",
            'shoulder_width': "Shoulder width must be between 30cm and 50cm",
            'arm_length': "Arm length must be between 50cm and 70cm"
        } 
