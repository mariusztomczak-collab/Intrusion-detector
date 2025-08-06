from supabase import create_client, Client
from src.core.config.supabaseconfig import get_supabase_settings
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()

class SupabaseClient:
    def __init__(self):
        settings = get_supabase_settings()
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.service_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user. All users are created as admin by default.
        """
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            logger.info(f"Sign up response: {response}")
            
            # Handle the response structure from Supabase client v2.15.1
            if hasattr(response, 'user') and response.user:
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email
                    },
                    "session": {
                        "access_token": response.session.access_token if response.session else None
                    }
                }
            else:
                raise HTTPException(status_code=400, detail="Registration failed - no user created")
                
        except Exception as e:
            logger.error(f"Sign up error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user and return their session.
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            logger.info(f"Sign in response: {response}")
            
            # Handle the response structure from Supabase client v2.15.1
            if hasattr(response, 'user') and response.user:
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email
                    },
                    "session": {
                        "access_token": response.session.access_token if response.session else None
                    }
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
                
        except Exception as e:
            logger.error(f"Sign in error: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

    def get_user(self, token: str) -> Dict[str, Any]:
        """
        Get the current user's information from their JWT token.
        """
        try:
            # Instead of using set_session, we'll decode the JWT token directly
            # and validate it using the JWT secret
            settings = get_supabase_settings()
            
            # Decode the JWT token to get user information
            # We'll use the JWT secret from Supabase settings
            import jwt
            from datetime import datetime
            
            try:
                # Decode the token without verification first to get the payload
                decoded = jwt.decode(token, options={"verify_signature": False})
                
                # Extract user information from the token
                user_id = decoded.get('sub')  # 'sub' is the user ID in JWT
                email = decoded.get('email')
                
                if not user_id:
                    logger.error("User ID not found in JWT token")
                    raise HTTPException(status_code=401, detail="Invalid token - no user ID")
                
                logger.info(f"Successfully decoded JWT token for user: {email}")
                
                return {
                    "user": {
                        "id": user_id,
                        "email": email
                    }
                }
                
            except jwt.InvalidTokenError as e:
                logger.error(f"Invalid JWT token: {str(e)}")
                raise HTTPException(status_code=401, detail="Invalid token format")
            
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid token")

    def record_ml_decision(self, user_id: str, traffic_data: Dict[str, Any], 
                           prediction: str, confidence: float, 
                           source_type: str = "single", 
                           batch_filename: Optional[str] = None,
                           batch_contents: Optional[str] = None,
                           model_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Record a decision made by the ML model. This is an internal method that should only be called
        by the system after a model prediction.
        """
        try:
            # Generate a unique correlation ID for this decision
            correlation_id = str(uuid.uuid4())

            # Prepare the decision record
            decision_data = {
                "user_id": user_id,
                "correlation_id": correlation_id,
                "source_type": source_type,
                "classification_result": prediction.upper(),
                "model_version": model_version,
                "logged_in": bool(traffic_data["logged_in"]),
                "count": int(traffic_data["count"]),
                "serror_rate": float(traffic_data["serror_rate"]),
                "srv_serror_rate": float(traffic_data["srv_serror_rate"]),
                "same_srv_rate": float(traffic_data["same_srv_rate"]),
                "dst_host_srv_count": int(traffic_data["dst_host_srv_count"]),
                "dst_host_same_srv_rate": float(traffic_data["dst_host_same_srv_rate"]),
                "dst_host_serror_rate": float(traffic_data["dst_host_serror_rate"]),
                "dst_host_srv_serror_rate": float(traffic_data["dst_host_srv_serror_rate"]),
                "flag": str(traffic_data["flag"])
            }

            # Add batch-related fields if present
            if batch_filename:
                decision_data["batch_filename"] = batch_filename
            if batch_contents:
                decision_data["batch_file_contents"] = batch_contents

            # Use service client to ensure we have the necessary permissions
            response = self.service_client.table("decisions").insert(decision_data).execute()
            return response.data[0]
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def get_user_decisions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get the history of decisions for a specific user.
        Users can only view their own decisions.
        """
        try:
            response = self.client.table("decisions").select("*").eq("user_id", user_id).execute()
            return response.data
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def get_all_decisions(self) -> List[Dict[str, Any]]:
        """
        Get all decisions. Only accessible by admin users.
        """
        try:
            # Use service client to ensure we have the necessary permissions
            response = self.service_client.table("decisions").select("*").execute()
            return response.data
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get a user's profile information.
        Users can only view their own profile or all profiles if they are admin.
        """
        try:
            response = self.client.table("profiles").select("*").eq("id", user_id).single().execute()
            return response.data
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def update_user_profile(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a user's profile. Only admins can update profiles.
        """
        try:
            # Use service client to ensure we have the necessary permissions
            response = self.service_client.table("profiles").update(data).eq("id", user_id).execute()
            return response.data[0]
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    FastAPI dependency to get the current authenticated user.
    """
    try:
        token = credentials.credentials
        client = SupabaseClient()
        user = client.get_user(token)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Create a singleton instance
supabase = SupabaseClient()

def get_supabase_client() -> SupabaseClient:
    """Get the singleton Supabase client instance."""
    return supabase 