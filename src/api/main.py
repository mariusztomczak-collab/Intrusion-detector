import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from src.api.schemas import (
    SingleDecisionRequest,
    BatchDecisionRequest,
    DecisionResponse,
    BatchDecisionResponse,
    ClassificationResult,
    NetworkTrafficFeatures,
    FEATURE_CATEGORIES,
    DecisionHistory,
    ErrorReport
)
from src.ml.pipeline.preprocessing.preprocessor import DataPreprocessor
import joblib
import os
import logging
import mlflow
import mlflow.sklearn
from src.api.middleware.correlation import CorrelationIdMiddleware, CORRELATION_ID
import structlog
from src.api.auth import verify_credentials
from src.core.supabaseclient import get_supabase_client
from src.api.routes.auth import router as auth_router
from src.api.routes.decisions import router as decisions_router, set_model_and_preprocessor
from src.utils.cache import init_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Network Intrusion Detection API",
    description="API for detecting malicious network traffic using machine learning",
    version="1.0.0"
)

# Add correlation ID middleware
app.add_middleware(CorrelationIdMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(decisions_router)

# Global variables for model and preprocessor
model = None
preprocessor = None

@app.on_event("startup")
async def startup_event():
    global model, preprocessor
    try:
        # Initialize Redis cache
        try:
            await init_cache()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis cache: {str(e)}")
            logger.info("Continuing without cache functionality")
        
        # Load model with fallback strategy
        logger.info("Attempting to load model...")
        model_name = os.getenv("MLFLOW_MODEL_NAME", "intrusion_detector")
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
        
        # Try MLflow first, then fallback to local model
        model_loaded = False
        
        # Strategy 1: Try MLflow Model Registry
        if tracking_uri and tracking_uri != "local":
            try:
                logger.info(f"Attempting to load from MLflow: {tracking_uri}")
                mlflow.set_tracking_uri(tracking_uri)
                
                client = mlflow.tracking.MlflowClient()
                versions = client.search_model_versions(f'name="{model_name}"')
                if versions:
                    latest_version = max(versions, key=lambda v: v.version)
                    model_uri = f"models:/{model_name}/{latest_version.version}"
                    model = mlflow.pyfunc.load_model(model_uri)
                    logger.info(f"Successfully loaded MLflow model '{model_name}' version '{latest_version.version}'")
                    model_loaded = True
                else:
                    logger.warning(f"No versions found for model {model_name} in MLflow")
            except Exception as e:
                logger.warning(f"Failed to load from MLflow: {str(e)}")
        
        # Strategy 2: Fallback to local model files
        if not model_loaded:
            try:
                logger.info("Attempting to load local model...")
                local_model_path = project_root / "artifacts" / "model.joblib"
                if local_model_path.exists():
                    model = joblib.load(local_model_path)
                    logger.info("Successfully loaded local model")
                    model_loaded = True
                else:
                    logger.warning(f"Local model not found at {local_model_path}")
            except Exception as e:
                logger.error(f"Failed to load local model: {str(e)}")
        
        # Strategy 3: Fallback to pickle model
        if not model_loaded:
            try:
                logger.info("Attempting to load pickle model...")
                pickle_model_path = project_root / "artifacts" / "model.pkl"
                if pickle_model_path.exists():
                    model = joblib.load(pickle_model_path)
                    logger.info("Successfully loaded pickle model")
                    model_loaded = True
                else:
                    logger.warning(f"Pickle model not found at {pickle_model_path}")
            except Exception as e:
                logger.error(f"Failed to load pickle model: {str(e)}")
        
        if not model_loaded:
            raise ValueError("No model could be loaded from any source")

        # Load preprocessor with similar fallback strategy
        logger.info("Loading preprocessor...")
        preprocessor_loaded = False
        
        # Try multiple preprocessor formats
        preprocessor_paths = [
            project_root / "artifacts" / "preprocessor.joblib",
            project_root / "artifacts" / "preprocessor.pkl",
            project_root / "artifacts" / "column_transformer.joblib"
        ]
        
        for preprocessor_path in preprocessor_paths:
            if preprocessor_path.exists():
                try:
                    preprocessor = DataPreprocessor()
                    column_transformer = joblib.load(preprocessor_path)
                    preprocessor.preprocessor = column_transformer
                    logger.info(f"Successfully loaded preprocessor from {preprocessor_path}")
                    preprocessor_loaded = True
                    break
                except Exception as e:
                    logger.warning(f"Failed to load preprocessor from {preprocessor_path}: {str(e)}")
                    continue
        
        if not preprocessor_loaded:
            raise FileNotFoundError(f"Preprocessor not found in any of: {[str(p) for p in preprocessor_paths]}")

        # Set model and preprocessor in the decisions router
        set_model_and_preprocessor(model, preprocessor)
        logger.info("Successfully injected model and preprocessor into decisions router")

    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise

async def save_decision(
    user_id: str,
    features: Dict[str, Any],
    result: str,
    correlation_id: str,
    source_type: str,
    model_version: Optional[str] = None
):
    """Save decision to database."""
    try:
        supabase = get_supabase_client()
        
        # Use the record_ml_decision method from SupabaseClient (now synchronous)
        supabase.record_ml_decision(
            user_id=user_id,
            traffic_data=features,
            prediction=result,
            confidence=0.0,  # We don't have confidence scores in this implementation
            source_type=source_type,
            model_version=model_version
        )
        
        logger.info(f"Successfully saved decision for correlation_id: {correlation_id}")
            
    except Exception as e:
        logger.error(f"Error saving decision: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "message": "Network Intrusion Detection API",
        "version": "1.0.0",
        "endpoints": {
            "/decisions/single": "Analyze single network traffic instance",
            "/decisions/batch": "Analyze multiple network traffic instances",
            "/decisions": "Get decision history",
            "/features": "Get information about available features"
        }
    }

@app.get("/features")
async def get_features():
    """Get information about available features and their categories."""
    return {
        "feature_categories": FEATURE_CATEGORIES,
        "description": "These are the most important features selected during model training"
    }

@app.post("/decisions/single", response_model=DecisionResponse)
async def analyze_single_traffic(
    request: SingleDecisionRequest,
    user_id: str = Depends(verify_credentials)
):
    """Analyze single network traffic instance."""
    try:
        if model is None or preprocessor is None:
            raise HTTPException(status_code=500, detail="Model or preprocessor not initialized")
        
        # Convert input to DataFrame
        features_df = pd.DataFrame([request.features.dict()])
        
        # Preprocess the traffic data
        features = preprocessor.transform(features_df)
        
        # Make prediction
        prediction = model.predict(features)[0]
        result = ClassificationResult.MALICIOUS if prediction == 1 else ClassificationResult.NORMAL
        
        # Prepare response
        response = DecisionResponse(
            classification_result=result,
            timestamp=datetime.utcnow(),
            correlation_id=request.correlation_id
        )
        
        # Save to database in background
        await save_decision(
            user_id=user_id,
            features=request.features.dict(),
            result=result,
            correlation_id=request.correlation_id,
            source_type="single",
            model_version=request.model_version
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing traffic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/decisions/batch", response_model=BatchDecisionResponse)
async def analyze_batch_traffic(
    request: BatchDecisionRequest,
    user_id: str = Depends(verify_credentials)
):
    """Analyze multiple network traffic instances."""
    try:
        if model is None or preprocessor is None:
            raise HTTPException(status_code=500, detail="Model or preprocessor not initialized")
        
        # Convert request to DataFrame
        traffic_data = pd.DataFrame([traffic.dict() for traffic in request.traffic_list])
        
        # Preprocess the data
        processed_data = preprocessor.transform(traffic_data)
        
        # Make predictions
        predictions = model.predict(processed_data)
        
        # Process results
        results = []
        errors = []
        successful = 0
        
        for i, (traffic, pred) in enumerate(zip(request.traffic_list, predictions)):
            try:
                result = ClassificationResult.MALICIOUS if pred == 1 else ClassificationResult.NORMAL
                correlation_id = f"{request.correlation_id}_{i}"
                
                # Save to database
                await save_decision(
                    user_id=user_id,
                    features=traffic.dict(),
                    result=result,
                    correlation_id=correlation_id,
                    source_type="batch",
                    model_version=request.model_version
                )
                
                results.append({
                    "correlation_id": correlation_id,
                    "classification_result": result
                })
                successful += 1
                
            except Exception as e:
                errors.append(ErrorReport(
                    correlation_id=f"{request.correlation_id}_{i}",
                    error=str(e)
                ))
        
        return BatchDecisionResponse(
            summary={
                "processed": len(request.traffic_list),
                "errors": len(errors),
                "successful": successful
            },
            report=results + [error.dict() for error in errors]
        )
        
    except Exception as e:
        logger.error(f"Error analyzing batch traffic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/decisions", response_model=List[DecisionHistory])
async def get_decisions(
    user_id: Optional[str] = None,
    source_type: Optional[str] = Query(None, regex="^(single|batch)$"),
    classification_result: Optional[str] = Query(None, regex="^(NORMAL|MALICIOUS)$"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: str = Query("timestamp desc", regex="^(timestamp|id) (asc|desc)$"),
    current_user_id: str = Depends(verify_credentials)
):
    """Get decision history with filtering and pagination."""
    try:
        supabase = get_supabase_client()
        
        # Build query
        query = supabase.table('decisions').select('*')
        
        # Apply filters
        if user_id:
            query = query.eq('user_id', user_id)
        if source_type:
            query = query.eq('source_type', source_type)
        if classification_result:
            query = query.eq('classification_result', classification_result)
            
        # Apply pagination and sorting
        query = query.range(offset, offset + limit - 1)
        sort_field, sort_order = sort.split()
        query = query.order(sort_field, desc=(sort_order == 'desc'))
        
        response = query.execute()
        
        if not response.data:
            return []
            
        return [DecisionHistory(**decision) for decision in response.data]
        
    except Exception as e:
        logger.error(f"Error fetching decisions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 