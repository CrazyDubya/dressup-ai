import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from typing import Dict, List, Tuple
import os

class MeasurementML:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = [
            'height', 'weight', 'age', 'body_type',
            'special_requirement', 'measurement_system',
            'seasonal_adjustment'
        ]
        self.target_columns = [
            'bust', 'underbust', 'waist', 'hips',
            'shoulder_width', 'arm_length'
        ]
        self.model_path = 'models/measurement_ml'
        self._load_or_create_models()

    def _load_or_create_models(self):
        """Load existing models or create new ones if they don't exist."""
        os.makedirs(self.model_path, exist_ok=True)
        
        for target in self.target_columns:
            model_file = f"{self.model_path}/{target}_model.joblib"
            scaler_file = f"{self.model_path}/{target}_scaler.joblib"
            
            if os.path.exists(model_file) and os.path.exists(scaler_file):
                self.models[target] = joblib.load(model_file)
                self.scalers[target] = joblib.load(scaler_file)
            else:
                self.models[target] = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                self.scalers[target] = StandardScaler()

    def _prepare_features(self, measurements: Dict) -> np.ndarray:
        """Prepare features for the ML model."""
        features = []
        for col in self.feature_columns:
            if col in measurements:
                if col in ['body_type', 'special_requirement', 'measurement_system']:
                    # Convert categorical variables to numeric
                    features.append(hash(measurements[col]) % 1000)
                else:
                    features.append(float(measurements[col]))
            else:
                features.append(0.0)
        return np.array(features).reshape(1, -1)

    def predict_measurements(self, measurements: Dict) -> Dict:
        """Predict missing measurements using ML models."""
        features = self._prepare_features(measurements)
        
        for target in self.target_columns:
            if target not in measurements:
                # Scale features
                scaled_features = self.scalers[target].transform(features)
                # Predict measurement
                prediction = self.models[target].predict(scaled_features)[0]
                measurements[target] = max(0, prediction)  # Ensure non-negative
        
        return measurements

    def train_models(self, training_data: List[Dict]):
        """Train the ML models with new data."""
        for target in self.target_columns:
            X = []
            y = []
            
            for data in training_data:
                if target in data:
                    features = self._prepare_features(data)
                    X.append(features[0])
                    y.append(data[target])
            
            if X and y:
                X = np.array(X)
                y = np.array(y)
                
                # Scale features
                self.scalers[target].fit(X)
                X_scaled = self.scalers[target].transform(X)
                
                # Train model
                self.models[target].fit(X_scaled, y)
                
                # Save model and scaler
                joblib.dump(self.models[target], f"{self.model_path}/{target}_model.joblib")
                joblib.dump(self.scalers[target], f"{self.model_path}/{target}_scaler.joblib")

    def evaluate_models(self, test_data: List[Dict]) -> Dict[str, float]:
        """Evaluate model performance on test data."""
        results = {}
        
        for target in self.target_columns:
            X = []
            y_true = []
            
            for data in test_data:
                if target in data:
                    features = self._prepare_features(data)
                    X.append(features[0])
                    y_true.append(data[target])
            
            if X and y_true:
                X = np.array(X)
                y_true = np.array(y_true)
                
                # Scale features
                X_scaled = self.scalers[target].transform(X)
                
                # Predict
                y_pred = self.models[target].predict(X_scaled)
                
                # Calculate metrics
                mae = np.mean(np.abs(y_true - y_pred))
                mse = np.mean((y_true - y_pred) ** 2)
                rmse = np.sqrt(mse)
                
                results[target] = {
                    'mae': mae,
                    'mse': mse,
                    'rmse': rmse
                }
        
        return results 