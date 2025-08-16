from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
from pydantic import BaseModel, Field, validator


class ClassificationResult(str, Enum):
    NORMAL = "NORMAL"
    MALICIOUS = "MALICIOUS"


class NetworkTrafficFeatures(BaseModel):
    """Schema for network traffic features."""

    # Numerical features
    logged_in: bool
    count: int = Field(ge=0)
    serror_rate: float = Field(ge=0, le=1)
    srv_serror_rate: float = Field(ge=0, le=1)
    same_srv_rate: float = Field(ge=0, le=1)
    dst_host_srv_count: int = Field(ge=0)
    dst_host_same_srv_rate: float = Field(ge=0, le=1)
    dst_host_serror_rate: float = Field(ge=0, le=1)
    dst_host_srv_serror_rate: float = Field(ge=0, le=1)

    # Categorical feature
    flag: str

    @validator("flag")
    def validate_flag(cls, v):
        """Validate that flag is either S0 or SF."""
        valid_flags = ["S0", "SF"]  # Add more flags if needed
        if v not in valid_flags:
            raise ValueError(f"flag must be one of {valid_flags}")
        return v


class SingleDecisionRequest(BaseModel):
    features: NetworkTrafficFeatures
    correlation_id: str
    model_version: Optional[str] = None


class BatchDecisionRequest(BaseModel):
    traffic_list: List[NetworkTrafficFeatures]
    correlation_id: str
    model_version: Optional[str] = None


class DecisionResponse(BaseModel):
    classification_result: ClassificationResult
    timestamp: datetime
    correlation_id: str


class BatchDecisionResponse(BaseModel):
    summary: Dict[str, int]  # processed, errors, successful
    report: List[Dict[str, Any]]  # List of results or errors


class ErrorReport(BaseModel):
    correlation_id: str
    error: str


class DecisionHistory(BaseModel):
    id: int
    user_id: str  # Changed from int to str to match Supabase UUID
    timestamp: datetime
    classification_result: ClassificationResult
    source_type: str
    correlation_id: str
    model_version: Optional[str]


# Feature categories for documentation
FEATURE_CATEGORIES = {
    "connection_features": ["logged_in", "count"],
    "error_rates": [
        "serror_rate",
        "srv_serror_rate",
        "dst_host_serror_rate",
        "dst_host_srv_serror_rate",
    ],
    "service_rates": ["same_srv_rate", "dst_host_same_srv_rate"],
    "host_features": ["dst_host_srv_count"],
    "protocol_features": ["flag"],
}
