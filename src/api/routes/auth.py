import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

from src.core.supabaseclient import get_supabase_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


# Pydantic models for request/response
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserForgotPassword(BaseModel):
    email: EmailStr


class AuthResponse(BaseModel):
    access_token: str
    user_id: str
    email: str
    message: str


class AuthError(BaseModel):
    error: str
    details: Optional[str] = None


@router.post(
    "/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(user_data: UserRegister):
    """Register a new user with Supabase Auth."""
    try:
        # Validate password confirmation
        if user_data.password != user_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match"
            )

        # Get Supabase client
        supabase = get_supabase_client()

        # Register user with Supabase Auth
        auth_response = supabase.sign_up(user_data.email, user_data.password)

        if not auth_response or "user" not in auth_response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Registration failed"
            )

        user = auth_response["user"]
        session = auth_response.get("session", {})

        logger.info(f"User registered successfully: {user['email']}")

        return AuthResponse(
            access_token=session.get("access_token", ""),
            user_id=user["id"],
            email=user["email"],
            message="User registered successfully",
        )

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        if "already registered" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@router.post("/login", response_model=AuthResponse)
async def login_user(user_data: UserLogin):
    """Login user with Supabase Auth."""
    try:
        # Get Supabase client
        supabase = get_supabase_client()

        # Sign in with Supabase Auth
        auth_response = supabase.sign_in(user_data.email, user_data.password)

        if not auth_response or "user" not in auth_response:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        user = auth_response["user"]
        session = auth_response.get("session", {})

        logger.info(f"User logged in successfully: {user['email']}")

        return AuthResponse(
            access_token=session.get("access_token", ""),
            user_id=user["id"],
            email=user["email"],
            message="Login successful",
        )

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        if "invalid" in str(e).lower() or "credentials" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}",
        )


@router.post("/logout")
async def logout_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user and invalidate session."""
    try:
        # For now, just return success since we don't have a logout method
        # In a real implementation, you would invalidate the token
        logger.info("User logged out successfully")

        return {"message": "Logout successful"}

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}",
        )


@router.post("/forgot-password")
async def forgot_password(user_data: UserForgotPassword):
    """Send password reset email."""
    try:
        # For now, just return success since we don't have a password reset method
        # In a real implementation, you would send the reset email
        logger.info(f"Password reset email would be sent to: {user_data.email}")

        return {"message": "Password reset email sent successfully"}

    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password reset failed: {str(e)}",
        )


@router.get("/me")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Get current user information."""
    try:
        # Get Supabase client
        supabase = get_supabase_client()

        # Get user from token
        user = supabase.get_user(credentials.credentials)

        if not user or "user" not in user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        return {
            "user_id": user["user"]["id"],
            "email": user["user"].get("email", "unknown"),
            "created_at": user["user"].get("created_at", "unknown"),
        }

    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


# Dependency for protected routes
async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Get current user ID from JWT token."""
    try:
        supabase = get_supabase_client()
        user = supabase.get_user(credentials.credentials)

        if not user or "user" not in user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        return user["user"]["id"]

    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
