import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import sys
import os
import joblib
from typing import List, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ml_algorithms.cardiovascular_risk.preprocessing import CardiovascularRiskPreprocessor
from ml_algorithms.cardiovascular_risk.model import CardiovascularRiskNeuralNetwork
from config.database import SessionLocal
from models.user import User

def get_all_user_ids() -> List[int]:
    """Get all user IDs from database"""
    db = SessionLocal()
    try:
        user_ids = db.query(User.ID).all()
        return [uid[0] for uid in user_ids]
    finally:
        db.close()

def train_cardiovascular_risk_model(user_ids: Optional[List[int]] = None, 
                                   test_size: float = 0.2,
                                   val_size: float = 0.2,
                                   epochs: int = 100,
                                   batch_size: int = 32,
                                   save_model: bool = True) -> dict:
    """
    Train cardiovascular risk classification model
    
    Args:
        user_ids: List of user IDs to train on. If None, uses all users
        test_size: Fraction of data to use for testing
        val_size: Fraction of training data to use for validation
        epochs: Number of training epochs
        batch_size: Training batch size
        save_model: Whether to save the trained model
    
    Returns:
        Dictionary containing training results and model performance
    """
    print("Starting cardiovascular risk model training...")
    
    # Get user IDs
    if user_ids is None:
        user_ids = get_all_user_ids()
    
    print(f"Training on {len(user_ids)} users")
    
    # Initialize preprocessor
    preprocessor = CardiovascularRiskPreprocessor()
    
    # Prepare dataset
    print("Preparing dataset...")
    X, y = preprocessor.prepare_dataset(user_ids)
    
    if len(X) == 0:
        raise ValueError("No valid data found. Check user IDs and database content.")
    
    print(f"Dataset prepared: {len(X)} samples, {len(X.columns)} features")
    print(f"Risk distribution: {y.value_counts().to_dict()}")
    
    # Split data
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_size/(1-test_size), random_state=42, stratify=y_temp
    )
    
    print(f"Data split: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
    
    # Fit preprocessor and transform data
    print("Preprocessing data...")
    X_train_scaled, y_train_encoded = preprocessor.fit_transform(X_train, y_train)
    X_val_scaled = preprocessor.transform(X_val)
    X_test_scaled = preprocessor.transform(X_test)
    
    y_val_encoded = preprocessor.label_encoder.transform(y_val)
    y_test_encoded = preprocessor.label_encoder.transform(y_test)
    
    # Initialize and train model
    print("Initializing neural network...")
    model = CardiovascularRiskNeuralNetwork(
        input_dim=X_train_scaled.shape[1],
        num_classes=len(preprocessor.label_encoder.classes_)
    )
    
    print("Training model...")
    training_history = model.train(
        X_train_scaled, y_train_encoded,
        X_val_scaled, y_val_encoded,
        epochs=epochs,
        batch_size=batch_size
    )
    
    # Evaluate model
    print("Evaluating model...")
    train_metrics = model.evaluate(X_train_scaled, y_train_encoded)
    val_metrics = model.evaluate(X_val_scaled, y_val_encoded)
    test_metrics = model.evaluate(X_test_scaled, y_test_encoded)
    
    # Get predictions for detailed analysis
    y_pred = model.predict(X_test_scaled)
    y_pred_labels = preprocessor.inverse_transform_labels(y_pred)
    
    # Print classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred_labels))
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred_labels))
    
    # Get feature importance
    print("Calculating feature importance...")
    feature_importance = model.get_feature_importance(X_test_scaled, preprocessor.feature_names)
    
    print("\nTop 10 Most Important Features:")
    for i, (feature, importance) in enumerate(list(feature_importance.items())[:10]):
        print(f"{i+1}. {feature}: {importance:.4f}")
    
    # Save model and preprocessor
    if save_model:
        model_dir = os.path.join(os.path.dirname(__file__), 'saved_models')
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, 'cardiovascular_risk_model.h5')
        preprocessor_path = os.path.join(model_dir, 'preprocessor.pkl')
        
        print(f"Saving model to {model_path}")
        model.save_model(model_path)
        
        print(f"Saving preprocessor to {preprocessor_path}")
        joblib.dump(preprocessor, preprocessor_path)
    
    # Prepare results
    results = {
        'model': model,
        'preprocessor': preprocessor,
        'training_history': training_history,
        'metrics': {
            'train': train_metrics,
            'validation': val_metrics,
            'test': test_metrics
        },
        'feature_importance': feature_importance,
        'classification_report': classification_report(y_test, y_pred_labels, output_dict=True),
        'confusion_matrix': confusion_matrix(y_test, y_pred_labels).tolist(),
        'risk_labels': preprocessor.label_encoder.classes_.tolist(),
        'feature_names': preprocessor.feature_names,
        'dataset_info': {
            'total_samples': len(X),
            'features_count': len(X.columns),
            'train_samples': len(X_train),
            'val_samples': len(X_val),
            'test_samples': len(X_test),
            'risk_distribution': y.value_counts().to_dict()
        }
    }
    
    print("\nTraining completed successfully!")
    print(f"Test Accuracy: {test_metrics['accuracy']:.4f}")
    print(f"Test F1 Score: {test_metrics['f1_score']:.4f}")
    
    return results

def main():
    """Main training function"""
    try:
        # Train model with default parameters
        results = train_cardiovascular_risk_model()
        
        # Print summary
        print("\n" + "="*50)
        print("TRAINING SUMMARY")
        print("="*50)
        print(f"Final Test Accuracy: {results['metrics']['test']['accuracy']:.4f}")
        print(f"Final Test F1 Score: {results['metrics']['test']['f1_score']:.4f}")
        print(f"Dataset Size: {results['dataset_info']['total_samples']} samples")
        print(f"Features: {results['dataset_info']['features_count']}")
        print(f"Risk Distribution: {results['dataset_info']['risk_distribution']}")
        
    except Exception as e:
        print(f"Error during training: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()