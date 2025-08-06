from typing import Dict, Any, Tuple
from enum import Enum

class FlagType(str, Enum):
    S0 = "S0"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    RSTO = "RSTO"
    RSTOS0 = "RSTOS0"
    RSTR = "RSTR"
    SH = "SH"
    SHR = "SHR"
    OTH = "OTH"

def validate_features(features: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate network traffic features.
    Returns (is_valid, error_message)
    """
    try:
        # Check required fields
        required_fields = {
            "logged_in": bool,
            "count": int,
            "serror_rate": float,
            "srv_serror_rate": float,
            "same_srv_rate": float,
            "dst_host_srv_count": int,
            "dst_host_same_srv_rate": float,
            "dst_host_serror_rate": float,
            "dst_host_srv_serror_rate": float,
            "flag": str
        }
        
        for field, field_type in required_fields.items():
            if field not in features:
                return False, f"Missing required field: {field}"
            if not isinstance(features[field], field_type):
                return False, f"Invalid type for {field}: expected {field_type.__name__}"
        
        # Validate numeric ranges
        if not 0 <= features["serror_rate"] <= 1:
            return False, "serror_rate must be between 0 and 1"
        if not 0 <= features["srv_serror_rate"] <= 1:
            return False, "srv_serror_rate must be between 0 and 1"
        if not 0 <= features["same_srv_rate"] <= 1:
            return False, "same_srv_rate must be between 0 and 1"
        if not 0 <= features["dst_host_same_srv_rate"] <= 1:
            return False, "dst_host_same_srv_rate must be between 0 and 1"
        if not 0 <= features["dst_host_serror_rate"] <= 1:
            return False, "dst_host_serror_rate must be between 0 and 1"
        if not 0 <= features["dst_host_srv_serror_rate"] <= 1:
            return False, "dst_host_srv_serror_rate must be between 0 and 1"
        
        # Validate count fields
        if features["count"] < 0:
            return False, "count must be non-negative"
        if features["dst_host_srv_count"] < 0:
            return False, "dst_host_srv_count must be non-negative"
        
        # Validate flag
        try:
            FlagType(features["flag"])
        except ValueError:
            return False, f"Invalid flag value. Must be one of: {', '.join([f.value for f in FlagType])}"
        
        return True, ""
        
    except Exception as e:
        return False, f"Validation error: {str(e)}" 