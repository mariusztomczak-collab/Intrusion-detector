#!/usr/bin/env python3
"""
Sample Model Creation Script for Intrusion Detector

This script creates a sample model and preprocessor for testing
the distribution functionality without requiring MLflow.

Usage:
    python scripts/create_sample_model.py
"""

import os
import sys
import joblib
import logging
from pathlib import Path
from datetime import datetime
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_sample_model():
    """Create a sample model and preprocessor for testing."""
    try:
        # Create artifacts directory
        artifacts_dir = project_root / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)
        
        logger.info("Creating sample model and preprocessor...")
        
        # Create sample data for training
        np.random.seed(42)
        n_samples = 1000
        
        # Generate sample features
        data = {
            'logged_in': np.random.choice([True, False], n_samples),
            'count': np.random.randint(1, 100, n_samples),
            'serror_rate': np.random.uniform(0, 1, n_samples),
            'srv_serror_rate': np.random.uniform(0, 1, n_samples),
            'same_srv_rate': np.random.uniform(0, 1, n_samples),
            'dst_host_srv_count': np.random.randint(1, 255, n_samples),
            'dst_host_same_srv_rate': np.random.uniform(0, 1, n_samples),
            'dst_host_serror_rate': np.random.uniform(0, 1, n_samples),
            'dst_host_srv_serror_rate': np.random.uniform(0, 1, n_samples),
            'flag': np.random.choice(['SF', 'S0', 'REJ', 'RSTO'], n_samples)
        }
        
        # Create labels (0 for normal, 1 for malicious)
        # Simple rule: high error rates and certain flags indicate malicious activity
        labels = np.zeros(n_samples)
        
        # Convert to pandas for easier boolean operations
        import pandas as pd
        df_data = pd.DataFrame(data)
        
        malicious_conditions = (
            (df_data['serror_rate'] > 0.5) |
            (df_data['srv_serror_rate'] > 0.5) |
            (df_data['flag'].isin(['REJ', 'RSTO'])) |
            (df_data['count'] > 50)
        )
        labels[malicious_conditions] = 1
        
        # Create preprocessor
        numerical_features = [
            'count', 'serror_rate', 'srv_serror_rate', 'same_srv_rate',
            'dst_host_srv_count', 'dst_host_same_srv_rate', 
            'dst_host_serror_rate', 'dst_host_srv_serror_rate'
        ]
        categorical_features = ['logged_in', 'flag']
        
        # Create column transformer
        from sklearn.preprocessing import OneHotEncoder
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numerical_features),
                ('cat', OneHotEncoder(drop='first', sparse_output=False), categorical_features)
            ],
            remainder='drop'
        )
        
        # Fit preprocessor
        X_processed = preprocessor.fit_transform(df_data)
        
        # Train a simple model
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_processed, labels)
        
        # Save model in multiple formats
        logger.info("Saving model files...")
        
        # Save as joblib (recommended)
        joblib_path = artifacts_dir / "model.joblib"
        joblib.dump(model, joblib_path)
        logger.info(f"Saved model as joblib: {joblib_path}")
        
        # Save as pickle (fallback)
        pickle_path = artifacts_dir / "model.pkl"
        joblib.dump(model, pickle_path)
        logger.info(f"Saved model as pickle: {pickle_path}")
        
        # Save preprocessor
        preprocessor_path = artifacts_dir / "preprocessor.joblib"
        joblib.dump(preprocessor, preprocessor_path)
        logger.info(f"Saved preprocessor: {preprocessor_path}")
        
        # Save as pickle for compatibility
        pickle_preprocessor_path = artifacts_dir / "preprocessor.pkl"
        joblib.dump(preprocessor, pickle_preprocessor_path)
        logger.info(f"Saved preprocessor as pickle: {pickle_preprocessor_path}")
        
        # Create metadata file
        metadata = {
            "model_name": "sample_intrusion_detector",
            "version": "1.0.0",
            "export_date": datetime.now().isoformat(),
            "model_files": [str(joblib_path), str(pickle_path)],
            "preprocessor_files": [str(preprocessor_path), str(pickle_preprocessor_path)],
            "features": {
                "numerical": numerical_features,
                "categorical": categorical_features
            },
            "model_type": "LogisticRegression",
            "training_samples": n_samples,
            "note": "This is a sample model for testing distribution functionality"
        }
        
        metadata_path = artifacts_dir / "model_metadata.json"
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata: {metadata_path}")
        
        # Create README for end users
        readme_content = f"""# Sample Model Files for Intrusion Detector

This directory contains sample machine learning model and preprocessor
for the Network Intrusion Detection application.

## Files:
- `model.joblib`: Main model file (recommended)
- `model.pkl`: Model file in pickle format (fallback)
- `preprocessor.joblib`: Data preprocessor
- `preprocessor.pkl`: Preprocessor in pickle format
- `model_metadata.json`: Model metadata and version information

## Usage:
The application will automatically load these files when starting.
No additional configuration is required.

## Model Information:
- Model Name: sample_intrusion_detector
- Version: 1.0.0
- Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Model Type: LogisticRegression
- Training Samples: {n_samples}

## Features:
- Numerical: {', '.join(numerical_features)}
- Categorical: {', '.join(categorical_features)}

## Notes:
- This is a SAMPLE model for testing purposes
- In production, replace with your actual trained model
- These files are required for the application to function
- Do not modify or delete these files
- Keep these files secure as they contain the trained model
"""
        
        readme_path = artifacts_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        logger.info(f"Saved README: {readme_path}")
        
        # Test model loading
        logger.info("Testing model loading...")
        test_model = joblib.load(joblib_path)
        test_preprocessor = joblib.load(preprocessor_path)
        
        # Test prediction
        test_data = pd.DataFrame({
            'logged_in': [True],
            'count': [10],
            'serror_rate': [0.1],
            'srv_serror_rate': [0.1],
            'same_srv_rate': [0.8],
            'dst_host_srv_count': [20],
            'dst_host_same_srv_rate': [0.8],
            'dst_host_serror_rate': [0.1],
            'dst_host_srv_serror_rate': [0.1],
            'flag': ['SF']
        })
        
        X_test = test_preprocessor.transform(test_data)
        prediction = test_model.predict(X_test)[0]
        probability = test_model.predict_proba(X_test)[0]
        
        logger.info(f"Test prediction: {prediction} (Normal: {probability[0]:.3f}, Malicious: {probability[1]:.3f})")
        
        logger.info("✅ Sample model creation completed successfully!")
        logger.info(f"📁 Model files are in: {artifacts_dir.absolute()}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create sample model: {str(e)}")
        return False

def main():
    success = create_sample_model()
    
    if success:
        print("\n🎉 Sample model creation successful!")
        print("📦 You can now test the distribution functionality.")
        print("🚀 The application will load these model files automatically.")
    else:
        print("\n❌ Sample model creation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 