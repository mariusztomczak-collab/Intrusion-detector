from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import logging
from src.api.schemas import (
    SingleDecisionRequest,
    BatchDecisionRequest,
    DecisionResponse,
    BatchDecisionResponse,
    ClassificationResult,
    DecisionHistory,
    ErrorReport
)
from src.api.routes.auth import get_current_user_id
from src.core.supabaseclient import get_supabase_client
from src.utils.cache import cache_decorator
from src.core.redisclient import get_redis_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/decisions", tags=["decisions"])

# Global variables for model and preprocessor (will be injected)
model = None
preprocessor = None

def set_model_and_preprocessor(ml_model, ml_preprocessor):
    """Set the global model and preprocessor for this router."""
    global model, preprocessor
    model = ml_model
    preprocessor = ml_preprocessor

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
        
        # Use the record_ml_decision method from SupabaseClient
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

@router.post("/single", response_model=DecisionResponse)
async def analyze_single_traffic_authenticated(
    request: SingleDecisionRequest,
    user_id: str = Depends(get_current_user_id),
    background_tasks: BackgroundTasks = None
):
    """Analyze single network traffic instance with authentication and caching."""
    try:
        if model is None or preprocessor is None:
            raise HTTPException(status_code=500, detail="Model or preprocessor not initialized")
        
        # Check cache first
        redis_client = get_redis_client()
        cached_response = redis_client.get_cached_response(request.features.dict(), user_id)
        
        if cached_response:
            logger.info(f"Cache hit for user {user_id}")
            return DecisionResponse(
                classification_result=cached_response["response"]["classification_result"],
                timestamp=datetime.utcnow(),
                correlation_id=request.correlation_id
            )
        
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
        
        # Cache the response
        try:
            redis_client.cache_response(
                request.features.dict(),
                user_id,
                {
                    "classification_result": result,
                    "timestamp": str(datetime.utcnow()),
                    "correlation_id": request.correlation_id
                }
            )
            logger.info(f"Cached response for user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to cache response: {str(e)}")
        
        # Save to database in background if background_tasks is available
        if background_tasks:
            background_tasks.add_task(
                save_decision,
                user_id=user_id,
                features=request.features.dict(),
                result=result,
                correlation_id=request.correlation_id,
                source_type="single",
                model_version=request.model_version
            )
        else:
            # Fallback to direct save
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
        logger.error(f"Error analyzing single traffic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/batch", response_model=BatchDecisionResponse)
async def analyze_batch_traffic_authenticated(
    request: BatchDecisionRequest,
    user_id: str = Depends(get_current_user_id),
    background_tasks: BackgroundTasks = None
):
    """Analyze multiple network traffic instances with authentication."""
    try:
        if model is None or preprocessor is None:
            raise HTTPException(status_code=500, detail="Model or preprocessor not initialized")
        
        results = []
        errors = []
        
        for i, features in enumerate(request.features):
            try:
                # Convert input to DataFrame
                features_df = pd.DataFrame([features.dict()])
                
                # Preprocess the traffic data
                processed_features = preprocessor.transform(features_df)
                
                # Make prediction
                prediction = model.predict(processed_features)[0]
                result = ClassificationResult.MALICIOUS if prediction == 1 else ClassificationResult.NORMAL
                
                # Create response
                decision_response = DecisionResponse(
                    classification_result=result,
                    timestamp=datetime.utcnow(),
                    correlation_id=f"{request.correlation_id}_{i}"
                )
                
                results.append(decision_response)
                
                # Save to database in background if background_tasks is available
                if background_tasks:
                    background_tasks.add_task(
                        save_decision,
                        user_id=user_id,
                        features=features.dict(),
                        result=result,
                        correlation_id=f"{request.correlation_id}_{i}",
                        source_type="batch",
                        model_version=request.model_version
                    )
                else:
                    # Fallback to direct save
                    await save_decision(
                        user_id=user_id,
                        features=features.dict(),
                        result=result,
                        correlation_id=f"{request.correlation_id}_{i}",
                        source_type="batch",
                        model_version=request.model_version
                    )
                
            except Exception as e:
                error = ErrorReport(
                    index=i,
                    error=str(e),
                    features=features.dict()
                )
                errors.append(error)
                logger.error(f"Error processing batch item {i}: {str(e)}")
        
        # Prepare response
        response = BatchDecisionResponse(
            results=results,
            total_processed=len(request.features),
            successful_predictions=len(results),
            errors=errors,
            correlation_id=request.correlation_id
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing batch traffic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@router.get("/", response_model=List[DecisionHistory])
async def get_decisions_authenticated(
    source_type: Optional[str] = Query(None, regex="^(single|batch)$"),
    classification_result: Optional[str] = Query(None, regex="^(NORMAL|MALICIOUS)$"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: str = Query("timestamp desc", regex="^(timestamp|id) (asc|desc)$"),
    user_id: str = Depends(get_current_user_id)
):
    """Get decision history for authenticated user."""
    try:
        supabase = get_supabase_client()
        
        # Build query
        query = supabase.table("decisions").select("*").eq("user_id", user_id)
        
        # Add filters
        if source_type:
            query = query.eq("source_type", source_type)
        if classification_result:
            query = query.eq("classification_result", classification_result)
        
        # Add sorting
        sort_parts = sort.split()
        if len(sort_parts) == 2:
            column, direction = sort_parts
            if direction.lower() == "desc":
                query = query.order(column, desc=True)
            else:
                query = query.order(column, desc=False)
        
        # Add pagination
        query = query.range(offset, offset + limit - 1)
        
        # Execute query
        response = query.execute()
        
        if response.data is None:
            return []
        
        # Convert to DecisionHistory objects
        decisions = []
        for decision in response.data:
            decisions.append(DecisionHistory(
                id=decision["id"],
                timestamp=decision["timestamp"],
                correlation_id=decision["correlation_id"],
                source_type=decision["source_type"],
                classification_result=decision["classification_result"],
                model_version=decision.get("model_version", "unknown")
            ))
        
        return decisions
        
    except Exception as e:
        logger.error(f"Error getting decisions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve decisions: {str(e)}")

@router.get("/cache/stats")
async def get_cache_stats(
    user_id: str = Depends(get_current_user_id)
):
    """Get Redis cache statistics."""
    try:
        redis_client = get_redis_client()
        stats = redis_client.get_cache_stats()
        return {
            "cache_stats": stats,
            "user_id": user_id,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache stats: {str(e)}")

@router.delete("/cache/clear")
async def clear_cache(
    user_id: str = Depends(get_current_user_id)
):
    """Clear all cached items."""
    try:
        redis_client = get_redis_client()
        success = redis_client.clear_cache()
        if success:
            return {"message": "Cache cleared successfully", "user_id": user_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear cache")
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}") 