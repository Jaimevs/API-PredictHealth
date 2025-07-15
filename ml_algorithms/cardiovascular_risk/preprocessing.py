import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from config.database import SessionLocal
from models.user import User
from models.person import Person
from models.health_profile import HealthProfile
from models.heart_measurement import HeartMeasurement
from models.physical_activity import PhysicalActivity

class CardiovascularRiskPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.imputer = SimpleImputer(strategy='median')
        self.feature_names = []
        
    def calculate_age(self, birth_date: datetime) -> int:
        """Calculate age from birth date"""
        today = datetime.now()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    def calculate_bmi(self, weight_kg: float, height_cm: float) -> float:
        """Calculate BMI"""
        if weight_kg is None or height_cm is None:
            return None
        height_m = height_cm / 100
        return weight_kg / (height_m ** 2)
    
    def extract_heart_features(self, heart_measurements: List[HeartMeasurement]) -> dict:
        """Extract aggregated heart measurement features"""
        if not heart_measurements:
            return {
                'avg_heart_rate': 0.0,  # Cambiar None por 0.0
                'max_heart_rate': 0.0,
                'min_heart_rate': 0.0,
                'heart_rate_variability': 0.0,
                'avg_systolic_bp': 0.0,
                'avg_diastolic_bp': 0.0,
                'avg_oxygen_saturation': 0.0,
                'avg_stress_level': 0.0,
                'high_heart_rate_episodes': 0,
                'low_heart_rate_episodes': 0
            }
        
        heart_rates = [m.Frecuencia_cardiaca for m in heart_measurements if m.Frecuencia_cardiaca]
        systolic_bp = [m.Presion_sistolica for m in heart_measurements if m.Presion_sistolica]
        diastolic_bp = [m.Presion_diastolica for m in heart_measurements if m.Presion_diastolica]
        oxygen_sat = [float(m.Saturacion_oxigeno) for m in heart_measurements if m.Saturacion_oxigeno]
        stress_levels = [m.Nivel_estres for m in heart_measurements if m.Nivel_estres]
        
        return {
            'avg_heart_rate': np.mean(heart_rates) if heart_rates else 0.0,
            'max_heart_rate': np.max(heart_rates) if heart_rates else 0.0,
            'min_heart_rate': np.min(heart_rates) if heart_rates else 0.0,
            'heart_rate_variability': np.std(heart_rates) if heart_rates else 0.0,
            'avg_systolic_bp': np.mean(systolic_bp) if systolic_bp else 0.0,
            'avg_diastolic_bp': np.mean(diastolic_bp) if diastolic_bp else 0.0,
            'avg_oxygen_saturation': np.mean(oxygen_sat) if oxygen_sat else 0.0,
            'avg_stress_level': np.mean(stress_levels) if stress_levels else 0.0,
            'high_heart_rate_episodes': sum(1 for hr in heart_rates if hr > 100),
            'low_heart_rate_episodes': sum(1 for hr in heart_rates if hr < 60)
        }
    
    def extract_activity_features(self, activities: List[PhysicalActivity]) -> dict:
        """Extract physical activity features"""
        if not activities:
            return {
                'avg_daily_steps': 0.0,  # Cambiar None por 0.0
                'avg_distance_km': 0.0,
                'avg_calories_burned': 0.0,
                'avg_active_minutes': 0.0,
                'activity_consistency': 0.0
            }
        
        steps = [a.Pasos for a in activities if a.Pasos]
        distances = [float(a.Distancia_km) for a in activities if a.Distancia_km]
        calories = [a.Calorias_quemadas for a in activities if a.Calorias_quemadas]
        active_minutes = [a.Minutos_actividad for a in activities if a.Minutos_actividad]
        
        return {
            'avg_daily_steps': np.mean(steps) if steps else 0.0,
            'avg_distance_km': np.mean(distances) if distances else 0.0,
            'avg_calories_burned': np.mean(calories) if calories else 0.0,
            'avg_active_minutes': np.mean(active_minutes) if active_minutes else 0.0,
            'activity_consistency': len(activities) / 30.0 if activities else 0.0  # Assuming 30-day period
        }
    
    def create_risk_label(self, health_profile: HealthProfile, heart_features: dict) -> str:
        """Create cardiovascular risk label based on risk factors"""
        risk_score = 0
        
        # Health profile risk factors
        if health_profile.Diabetico:
            risk_score += 2
        if health_profile.Hipertenso:
            risk_score += 2
        if health_profile.Fumador:
            risk_score += 1
        if health_profile.Historial_cardiaco:
            risk_score += 3
        
        # BMI risk factor
        if health_profile.Peso_kg and health_profile.Altura_cm:
            bmi = self.calculate_bmi(float(health_profile.Peso_kg), float(health_profile.Altura_cm))
            if bmi and bmi >= 30:
                risk_score += 1
        
        # Heart measurement risk factors
        if heart_features['avg_systolic_bp'] and heart_features['avg_systolic_bp'] >= 140:
            risk_score += 2
        if heart_features['avg_diastolic_bp'] and heart_features['avg_diastolic_bp'] >= 90:
            risk_score += 2
        if heart_features['high_heart_rate_episodes'] > 10:
            risk_score += 1
        
        # Risk classification
        if risk_score >= 6:
            return 'HIGH'
        elif risk_score >= 3:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def fetch_user_data(self, user_id: int, days_back: int = 30) -> dict:
        """Fetch user data from database"""
        db = SessionLocal()
        try:
            # Get user and related data
            user = db.query(User).filter(User.ID == user_id).first()
            if not user:
                return None
            
            person = user.person
            health_profile = user.health_profile
            
            # Get recent heart measurements
            cutoff_date = datetime.now() - timedelta(days=days_back)
            heart_measurements = db.query(HeartMeasurement).filter(
                HeartMeasurement.Usuario_ID == user_id,
                HeartMeasurement.Timestamp_medicion >= cutoff_date
            ).all()
            
            # Get recent physical activities
            activities = db.query(PhysicalActivity).filter(
                PhysicalActivity.Usuario_ID == user_id,
                PhysicalActivity.Fecha_Registro >= cutoff_date
            ).all()
            
            return {
                'user': user,
                'person': person,
                'health_profile': health_profile,
                'heart_measurements': heart_measurements,
                'activities': activities
            }
        finally:
            db.close()
    
    def preprocess_user_data(self, user_data: dict) -> dict:
        """Preprocess single user data"""
        person = user_data['person']
        health_profile = user_data['health_profile']
        heart_measurements = user_data['heart_measurements']
        activities = user_data['activities']
        
        # Extract features
        heart_features = self.extract_heart_features(heart_measurements)
        activity_features = self.extract_activity_features(activities)
        
        # Create feature vector
        features = {
            # Demographics
            'age': self.calculate_age(person.Fecha_Nacimiento),
            'gender_male': 1 if person.Genero.value == 'H' else 0,
            'gender_female': 1 if person.Genero.value == 'M' else 0,
            
            # Health profile
            'weight_kg': float(health_profile.Peso_kg) if health_profile.Peso_kg else 0.0,
            'height_cm': float(health_profile.Altura_cm) if health_profile.Altura_cm else 0.0,
            'bmi': self.calculate_bmi(
                float(health_profile.Peso_kg) if health_profile.Peso_kg else None,
                float(health_profile.Altura_cm) if health_profile.Altura_cm else None
            ) or 0.0,  # Usar 0.0 si BMI es None
            'is_smoker': 1 if health_profile.Fumador else 0,
            'is_diabetic': 1 if health_profile.Diabetico else 0,
            'is_hypertensive': 1 if health_profile.Hipertenso else 0,
            'has_cardiac_history': 1 if health_profile.Historial_cardiaco else 0,
            
            # Heart measurements
            **heart_features,
            
            # Physical activity
            **activity_features
        }
        
        # Create risk label
        risk_label = self.create_risk_label(health_profile, heart_features)
        
        return features, risk_label
    
    def prepare_dataset(self, user_ids: List[int]) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare dataset from multiple users"""
        all_features = []
        all_labels = []
        
        for user_id in user_ids:
            user_data = self.fetch_user_data(user_id)
            if user_data and user_data['health_profile']:
                features, label = self.preprocess_user_data(user_data)
                all_features.append(features)
                all_labels.append(label)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_features)
        labels = pd.Series(all_labels)
        
        print(f"DataFrame shape before imputation: {df.shape}")
        print(f"Columns with null values: {df.isnull().sum().sum()}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Handle missing values more carefully
        # Fill remaining NaN values with 0 before using imputer
        df = df.fillna(0.0)
        
        # Store feature names BEFORE any transformation
        self.feature_names = df.columns.tolist()
        
        print(f"DataFrame shape after fillna: {df.shape}")
        print(f"Feature names: {len(self.feature_names)}")
        
        return df, labels
    
    def fit_transform(self, X: pd.DataFrame, y: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
        """Fit preprocessor and transform data"""
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        return X_scaled, y_encoded
    
    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """Transform new data"""
        # Handle missing values by filling with 0
        X_filled = X.fillna(0.0)
        
        # Scale features
        X_scaled = self.scaler.transform(X_filled)
        
        return X_scaled
    
    def inverse_transform_labels(self, y_encoded: np.ndarray) -> List[str]:
        """Convert encoded labels back to original"""
        return self.label_encoder.inverse_transform(y_encoded)