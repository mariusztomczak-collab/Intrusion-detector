import gradio as gr
import logging
import requests
from typing import Optional, Dict, Any, Callable
from functools import wraps

logger = logging.getLogger(__name__)

class AuthGuard:
    """Authentication guard for protecting routes and components."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.auth_state = None
    
    def is_authenticated(self, auth_state: Optional[Dict[str, Any]]) -> bool:
        """Check if user is authenticated."""
        if not auth_state:
            return False
        
        return auth_state.get("is_authenticated", False) and auth_state.get("token")
    
    def validate_token(self, token: str) -> bool:
        """Validate JWT token with backend."""
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.api_base_url}/auth/me",
                headers=headers
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return False
    
    def require_auth(self, redirect_to_login: bool = True):
        """Decorator to require authentication for functions."""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Extract auth_state from kwargs or args
                auth_state = kwargs.get('auth_state')
                if not auth_state:
                    # Try to find auth_state in args
                    for arg in args:
                        if isinstance(arg, dict) and 'is_authenticated' in arg:
                            auth_state = arg
                            break
                
                if not self.is_authenticated(auth_state):
                    if redirect_to_login:
                        logger.warning("Unauthorized access attempt - redirecting to login")
                        return {
                            "error": "Musisz być zalogowany, aby korzystać z tej funkcji.",
                            "redirect_to_login": True
                        }
                    else:
                        logger.warning("Unauthorized access attempt - access denied")
                        return {
                            "error": "Brak uprawnień dostępu.",
                            "access_denied": True
                        }
                
                # Validate token with backend
                if not self.validate_token(auth_state.get("token", "")):
                    logger.warning("Invalid token - redirecting to login")
                    return {
                        "error": "Sesja wygasła. Zaloguj się ponownie.",
                        "redirect_to_login": True
                    }
                
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def protect_component(self, component_func: Callable, auth_state: gr.State):
        """Protect a Gradio component with authentication."""
        def protected_wrapper(*args, **kwargs):
            if not self.is_authenticated(auth_state.value):
                return {
                    "error": "Musisz być zalogowany, aby korzystać z tej funkcji.",
                    "redirect_to_login": True
                }
            
            return component_func(*args, **kwargs)
        
        return protected_wrapper
    
    def create_auth_middleware(self):
        """Create authentication middleware for Gradio app."""
        def middleware(event: gr.SelectData, auth_state: gr.State):
            """Middleware to check authentication on tab changes."""
            # Allow access to auth tabs (0, 1, 2) without authentication
            if event.index in [0, 1, 2]:
                return gr.update(selected=event.index)
            
            # Require authentication for protected tabs (3+)
            if not self.is_authenticated(auth_state.value):
                logger.warning(f"Unauthorized access attempt to tab {event.index}")
                return gr.update(selected=0)  # Redirect to login tab
            
            return gr.update(selected=event.index)
        
        return middleware

# Global auth guard instance
auth_guard = AuthGuard()

def require_authentication(redirect_to_login: bool = True):
    """Decorator to require authentication."""
    return auth_guard.require_auth(redirect_to_login)

def is_user_authenticated(auth_state: Optional[Dict[str, Any]]) -> bool:
    """Check if user is authenticated."""
    return auth_guard.is_authenticated(auth_state)

def validate_user_token(token: str) -> bool:
    """Validate user token."""
    return auth_guard.validate_token(token) 