import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import numpy as np
from typing import Tuple, List
import joblib
import os

class CardiovascularRiskNeuralNetwork:
    def __init__(self, input_dim: int, num_classes: int = 3):
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.model = None
        self.history = None
        
    def build_model(self) -> tf.keras.Model:
        """Build neural network architecture"""
        model = Sequential([
            # Input layer - Usar Input() en lugar de input_shape
            Input(shape=(self.input_dim,)),
            
            # Hidden layers
            Dense(128, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(32, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            
            Dense(16, activation='relu'),
            Dropout(0.2),
            
            # Output layer
            Dense(self.num_classes, activation='softmax')
        ])
        
        # Compilar solo con accuracy para evitar problemas de métricas
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']  # Solo usar accuracy
        )
        
        self.model = model
        return model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              X_val: np.ndarray, y_val: np.ndarray,
              epochs: int = 100, batch_size: int = 32) -> dict:
        """Train the neural network"""
        
        if self.model is None:
            self.build_model()
        
        # Callbacks
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True,
            verbose=1
        )
        
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=10,
            min_lr=0.00001,
            verbose=1
        )
        
        # Train model
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stopping, reduce_lr],
            verbose=1
        )
        
        return self.history.history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        predictions = self.model.predict(X)
        return np.argmax(predictions, axis=1)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get prediction probabilities"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        return self.model.predict(X)
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        """Evaluate model performance"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Get predictions
        y_pred = self.predict(X_test)
        y_proba = self.predict_proba(X_test)
        
        # Calculate metrics manually usando sklearn
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # Calculate loss manually
        loss = tf.keras.losses.sparse_categorical_crossentropy(y_test, y_proba).numpy().mean()
        
        return {
            'loss': float(loss),
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1)
        }
    
    def save_model(self, filepath: str):
        """Save trained model"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save model
        self.model.save(filepath)
        
        # Save model metadata
        metadata = {
            'input_dim': self.input_dim,
            'num_classes': self.num_classes,
            'history': self.history.history if self.history else None
        }
        
        joblib.dump(metadata, filepath.replace('.h5', '_metadata.pkl'))
    
    def load_model(self, filepath: str):
        """Load trained model"""
        # Load model
        self.model = tf.keras.models.load_model(filepath)
        
        # Load metadata
        metadata = joblib.load(filepath.replace('.h5', '_metadata.pkl'))
        self.input_dim = metadata['input_dim']
        self.num_classes = metadata['num_classes']
        
        # Recreate history object if available
        if metadata['history']:
            self.history = type('History', (), {'history': metadata['history']})()
    
    def get_feature_importance(self, X: np.ndarray, feature_names: List[str], 
                             method: str = 'permutation') -> dict:
        """Get feature importance using permutation importance"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Get baseline predictions
        baseline_pred = self.predict(X)
        baseline_accuracy = np.mean(baseline_pred == baseline_pred)  # Always 1, but for consistency
        
        importances = {}
        
        if method == 'permutation':
            # For each feature, permute its values and measure accuracy drop
            for i, feature_name in enumerate(feature_names):
                X_permuted = X.copy()
                np.random.shuffle(X_permuted[:, i])
                
                permuted_pred = self.predict(X_permuted)
                # Calculate accuracy based on consistency with baseline
                permuted_accuracy = np.mean(permuted_pred == baseline_pred) 
                
                importance = 1.0 - permuted_accuracy  # Higher when permutation causes more change
                importances[feature_name] = importance
        
        # Sort by importance
        sorted_importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
        
        return sorted_importances
    
    def summary(self):
        """Print model summary"""
        if self.model is None:
            print("Model not built yet.")
            return
        
        self.model.summary()
    
    def plot_training_history(self):
        """Plot training history"""
        if self.history is None:
            print("No training history available.")
            return
        
        try:
            import matplotlib.pyplot as plt
            
            fig, axes = plt.subplots(1, 2, figsize=(12, 5))
            
            # Plot loss
            axes[0].plot(self.history.history['loss'], label='Training Loss')
            axes[0].plot(self.history.history['val_loss'], label='Validation Loss')
            axes[0].set_title('Model Loss')
            axes[0].set_xlabel('Epoch')
            axes[0].set_ylabel('Loss')
            axes[0].legend()
            
            # Plot accuracy
            axes[1].plot(self.history.history['accuracy'], label='Training Accuracy')
            axes[1].plot(self.history.history['val_accuracy'], label='Validation Accuracy')
            axes[1].set_title('Model Accuracy')
            axes[1].set_xlabel('Epoch')
            axes[1].set_ylabel('Accuracy')
            axes[1].legend()
            
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            print("Matplotlib not available. Install matplotlib to plot training history.")
    
    def get_risk_explanation(self, X: np.ndarray, feature_names: List[str], 
                           risk_prediction: int) -> dict:
        """Get explanation for risk prediction"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Get prediction probabilities
        probabilities = self.predict_proba(X)
        
        # Risk labels
        risk_labels = ['HIGH', 'LOW', 'MEDIUM']  # Ajustar según la codificación de labels
        
        # Create explanation
        explanation = {
            'predicted_risk': risk_labels[risk_prediction],
            'confidence': float(np.max(probabilities[0])),
            'risk_probabilities': {
                risk_labels[i]: float(probabilities[0][i]) for i in range(len(risk_labels))
            },
            'key_risk_factors': []
        }
        
        # Identify key risk factors based on feature values
        feature_values = X[0]
        for i, (feature_name, value) in enumerate(zip(feature_names, feature_values)):
            if 'diabetic' in feature_name.lower() and value > 0.5:
                explanation['key_risk_factors'].append('Diabetes')
            elif 'hypertensive' in feature_name.lower() and value > 0.5:
                explanation['key_risk_factors'].append('Hypertension')
            elif 'smoker' in feature_name.lower() and value > 0.5:
                explanation['key_risk_factors'].append('Smoking')
            elif 'cardiac_history' in feature_name.lower() and value > 0.5:
                explanation['key_risk_factors'].append('Cardiac History')
            elif 'bmi' in feature_name.lower() and value > 30:
                explanation['key_risk_factors'].append('High BMI')
            elif 'systolic_bp' in feature_name.lower() and value > 140:
                explanation['key_risk_factors'].append('High Systolic Blood Pressure')
            elif 'diastolic_bp' in feature_name.lower() and value > 90:
                explanation['key_risk_factors'].append('High Diastolic Blood Pressure')
        
        return explanation