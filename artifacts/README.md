# Sample Model Files for Intrusion Detector

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
- Export Date: 2025-08-06 10:45:54
- Model Type: LogisticRegression
- Training Samples: 1000

## Features:
- Numerical: count, serror_rate, srv_serror_rate, same_srv_rate, dst_host_srv_count, dst_host_same_srv_rate, dst_host_serror_rate, dst_host_srv_serror_rate
- Categorical: logged_in, flag

## Notes:
- This is a SAMPLE model for testing purposes
- In production, replace with your actual trained model
- These files are required for the application to function
- Do not modify or delete these files
- Keep these files secure as they contain the trained model
