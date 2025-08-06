#!/usr/bin/env python3
"""
Model Export Script for Intrusion Detector

This script exports the trained model and preprocessor from MLflow
to local files that can be bundled with the application for end users.

Usage:
    python scripts/export_model.py [--model-name MODEL_NAME] [--output-dir OUTPUT_DIR]
"""

import os
import sys
import argparse
import joblib
import mlflow
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.ml.pipeline.preprocessing.preprocessor import DataPreprocessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def export_model(model_name: str = "intrusion_detector", 
                output_dir: str = "artifacts",
                tracking_uri: str = "http://localhost:5000"):
    """
    Export model and preprocessor from MLflow to local files.
    
    Args:
        model_name (str): Name of the model in MLflow registry
        output_dir (str): Directory to save exported files
        tracking_uri (str): MLflow tracking URI
    """
    try:
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Set MLflow tracking URI
        mlflow.set_tracking_uri(tracking_uri)
        
        # Get the latest model version
        logger.info(f"Connecting to MLflow at {tracking_uri}")
        client = mlflow.tracking.MlflowClient()
        versions = client.search_model_versions(f'name="{model_name}"')
        
        if not versions:
            raise ValueError(f"No versions found for model {model_name}")
        
        # Get the latest version
        latest_version = max(versions, key=lambda v: v.version)
        logger.info(f"Found model version {latest_version.version}")
        
        # Download model
        logger.info("Downloading model...")
        model_uri = f"models:/{model_name}/{latest_version.version}"
        model = mlflow.pyfunc.load_model(model_uri)
        
        # Save model in multiple formats for compatibility
        model_paths = []
        
        # Save as joblib (recommended)
        joblib_path = output_path / "model.joblib"
        joblib.dump(model, joblib_path)
        model_paths.append(joblib_path)
        logger.info(f"Saved model as joblib: {joblib_path}")
        
        # Save as pickle (fallback)
        pickle_path = output_path / "model.pkl"
        joblib.dump(model, pickle_path)
        model_paths.append(pickle_path)
        logger.info(f"Saved model as pickle: {pickle_path}")
        
        # Export preprocessor if it exists
        logger.info("Checking for preprocessor...")
        preprocessor_path = project_root / "artifacts" / "preprocessor.joblib"
        
        if preprocessor_path.exists():
            # Copy preprocessor to output directory
            output_preprocessor_path = output_path / "preprocessor.joblib"
            import shutil
            shutil.copy2(preprocessor_path, output_preprocessor_path)
            logger.info(f"Copied preprocessor: {output_preprocessor_path}")
            
            # Also save as pickle for compatibility
            pickle_preprocessor_path = output_path / "preprocessor.pkl"
            try:
                preprocessor = joblib.load(preprocessor_path)
                joblib.dump(preprocessor, pickle_preprocessor_path)
                logger.info(f"Saved preprocessor as pickle: {pickle_preprocessor_path}")
            except Exception as e:
                logger.warning(f"Could not save preprocessor as pickle: {e}")
        else:
            logger.warning("Preprocessor not found, skipping preprocessor export")
        
        # Create metadata file
        metadata = {
            "model_name": model_name,
            "version": latest_version.version,
            "export_date": datetime.now().isoformat(),
            "model_files": [str(p) for p in model_paths],
            "mlflow_tracking_uri": tracking_uri,
            "model_uri": model_uri
        }
        
        metadata_path = output_path / "model_metadata.json"
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata: {metadata_path}")
        
        # Create README for end users
        readme_content = f"""# Model Files for Intrusion Detector

This directory contains the exported machine learning model and preprocessor
for the Network Intrusion Detection application.

## Files:
- `model.joblib`: Main model file (recommended)
- `model.pkl`: Model file in pickle format (fallback)
- `preprocessor.joblib`: Data preprocessor (if available)
- `preprocessor.pkl`: Preprocessor in pickle format (if available)
- `model_metadata.json`: Model metadata and version information

## Usage:
The application will automatically load these files when starting.
No additional configuration is required.

## Model Information:
- Model Name: {model_name}
- Version: {latest_version.version}
- Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Notes:
- These files are required for the application to function
- Do not modify or delete these files
- Keep these files secure as they contain the trained model
"""
        
        readme_path = output_path / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        logger.info(f"Saved README: {readme_path}")
        
        logger.info("✅ Model export completed successfully!")
        logger.info(f"📁 Exported files are in: {output_path.absolute()}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to export model: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Export model from MLflow for distribution")
    parser.add_argument("--model-name", default="intrusion_detector", 
                       help="Name of the model in MLflow registry")
    parser.add_argument("--output-dir", default="artifacts", 
                       help="Output directory for exported files")
    parser.add_argument("--tracking-uri", default="http://localhost:5000",
                       help="MLflow tracking URI")
    
    args = parser.parse_args()
    
    success = export_model(
        model_name=args.model_name,
        output_dir=args.output_dir,
        tracking_uri=args.tracking_uri
    )
    
    if success:
        print("\n🎉 Model export successful!")
        print("📦 You can now distribute the application with these model files.")
        print("🚀 End users will be able to run the application without MLflow.")
    else:
        print("\n❌ Model export failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 