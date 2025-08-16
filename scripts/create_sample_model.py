#!/usr/bin/env python3
"""
Create Sample Model Script for CI/CD Pipeline

This script creates sample machine learning models and preprocessors
for testing purposes during CI/CD pipeline execution.
"""

import os
import sys
import joblib
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def create_sample_model():
    """Create a sample logistic regression model for testing."""
    print("🔧 Creating sample ML model for CI/CD testing...")
    
    # Create sample data
    np.random.seed(42)
    n_samples = 100
    
    # Generate synthetic features
    numerical_features = np.random.randn(n_samples, 8)  # 8 numerical features
    categorical_features = np.random.randint(0, 2, (n_samples, 2))  # 2 binary features
    
    # Combine features
    X = np.hstack([numerical_features, categorical_features])
    
    # Create synthetic labels (binary classification)
    y = (np.sum(numerical_features, axis=1) > 0).astype(int)
    
    # Create preprocessor
    numerical_transformer = Pipeline([
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline([
        ('encoder', OneHotEncoder(drop='first', sparse_output=False))
    ])
    
    # Combine transformers
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, list(range(8))),
            ('cat', categorical_transformer, list(range(8, 10)))
        ],
        remainder='drop'
    )
    
    # Create and train model
    model = LogisticRegression(random_state=42, max_iter=1000)
    
    # Fit preprocessor and transform data
    X_transformed = preprocessor.fit_transform(X)
    
    # Fit model
    model.fit(X_transformed, y)
    
    # Create artifacts directory if it doesn't exist
    artifacts_dir = project_root / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    
    # Save model and preprocessor
    model_path = artifacts_dir / "model.joblib"
    preprocessor_path = artifacts_dir / "preprocessor.joblib"
    
    joblib.dump(model, model_path)
    joblib.dump(preprocessor, preprocessor_path)
    
    # Create fallback pickle files
    model_pkl_path = artifacts_dir / "model.pkl"
    preprocessor_pkl_path = artifacts_dir / "preprocessor.pkl"
    
    joblib.dump(model, model_pkl_path)
    joblib.dump(preprocessor, preprocessor_pkl_path)
    
    # Create model metadata
    metadata = {
        "model_name": "sample_intrusion_detector",
        "version": "1.0.0",
        "export_date": "2025-08-16",
        "model_type": "LogisticRegression",
        "training_samples": n_samples,
        "features": {
            "numerical": 8,
            "categorical": 2
        },
        "accuracy": model.score(X_transformed, y)
    }
    
    # Save metadata
    import json
    metadata_path = artifacts_dir / "model_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Sample model created successfully!")
    print(f"📁 Model saved to: {model_path}")
    print(f"📁 Preprocessor saved to: {preprocessor_path}")
    print(f"📁 Metadata saved to: {metadata_path}")
    print(f"🎯 Model accuracy: {metadata['accuracy']:.3f}")
    
    return True

if __name__ == "__main__":
    try:
        success = create_sample_model()
        if success:
            print("🎉 Sample model creation completed successfully!")
            sys.exit(0)
        else:
            print("❌ Sample model creation failed!")
            sys.exit(1)
    except Exception as e:
        print(f"💥 Error creating sample model: {str(e)}")
        sys.exit(1)
