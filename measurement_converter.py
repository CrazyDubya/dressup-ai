from typing import Dict, Union
from enum import Enum

class MeasurementSystem(Enum):
    METRIC = "metric"      # cm, kg
    IMPERIAL = "imperial"  # inches, lbs
    ASIAN = "asian"       # cm, kg with different proportions
    EUROPEAN = "european"  # cm, kg with different proportions

class MeasurementConverter:
    def __init__(self):
        # Conversion factors
        self.conversion_factors = {
            'metric_to_imperial': {
                'length': 0.393701,  # cm to inches
                'weight': 2.20462    # kg to lbs
            },
            'imperial_to_metric': {
                'length': 2.54,      # inches to cm
                'weight': 0.453592   # lbs to kg
            }
        }
        
        # Measurement types
        self.length_measurements = {
            'height', 'bust', 'underbust', 'waist', 
            'hips', 'shoulder_width', 'arm_length'
        }
        self.weight_measurements = {'weight'}
        
        # Cultural adjustment factors
        self.cultural_adjustments = {
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

    def convert_measurements(self, measurements: Dict, 
                           target_system: Union[str, MeasurementSystem]) -> Dict:
        """Convert measurements to the target system."""
        if isinstance(target_system, str):
            target_system = MeasurementSystem(target_system)
        
        converted = measurements.copy()
        
        # Apply cultural adjustments first
        if target_system in [MeasurementSystem.ASIAN, MeasurementSystem.EUROPEAN]:
            adjustments = self.cultural_adjustments[target_system]
            for key, factor in adjustments.items():
                if key in converted:
                    converted[key] *= factor
        
        # Convert units
        if target_system == MeasurementSystem.IMPERIAL:
            # Convert metric to imperial
            for key in self.length_measurements:
                if key in converted:
                    converted[key] *= self.conversion_factors['metric_to_imperial']['length']
            for key in self.weight_measurements:
                if key in converted:
                    converted[key] *= self.conversion_factors['metric_to_imperial']['weight']
        elif target_system == MeasurementSystem.METRIC:
            # Convert imperial to metric
            for key in self.length_measurements:
                if key in converted:
                    converted[key] *= self.conversion_factors['imperial_to_metric']['length']
            for key in self.weight_measurements:
                if key in converted:
                    converted[key] *= self.conversion_factors['imperial_to_metric']['weight']
        
        return converted

    def get_unit_labels(self, system: Union[str, MeasurementSystem]) -> Dict[str, str]:
        """Get unit labels for the specified system."""
        if isinstance(system, str):
            system = MeasurementSystem(system)
        
        if system == MeasurementSystem.IMPERIAL:
            return {
                'height': 'inches',
                'bust': 'inches',
                'underbust': 'inches',
                'waist': 'inches',
                'hips': 'inches',
                'shoulder_width': 'inches',
                'arm_length': 'inches',
                'weight': 'lbs'
            }
        else:
            return {
                'height': 'cm',
                'bust': 'cm',
                'underbust': 'cm',
                'waist': 'cm',
                'hips': 'cm',
                'shoulder_width': 'cm',
                'arm_length': 'cm',
                'weight': 'kg'
            }

    def format_measurement(self, value: float, unit: str) -> str:
        """Format a measurement value with its unit."""
        if unit in ['cm', 'inches']:
            return f"{value:.1f} {unit}"
        elif unit in ['kg', 'lbs']:
            return f"{value:.1f} {unit}"
        else:
            return str(value) 
