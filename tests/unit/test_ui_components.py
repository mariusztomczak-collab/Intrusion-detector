"""
Unit tests for UI components (Gradio interface).
"""

from unittest.mock import MagicMock, Mock, patch

import gradio as gr
import pytest


class TestUnifiedAppUI:
    """Test suite for UnifiedApp UI components."""
    
    def setup_method(self):
        """Setup test environment."""
        from src.ui.unified_app import UnifiedApp
        self.app = UnifiedApp()
    
    def test_app_initialization(self):
        """Test UnifiedApp initialization."""
        assert self.app is not None
        assert hasattr(self.app, 'api_base_url')
        assert hasattr(self.app, 'auth_state')
    
    def test_validate_email_valid(self):
        """Test email validation with valid email."""
        assert self.app.validate_email("test@example.com") == True
        assert self.app.validate_email("user.name@domain.co.uk") == True
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid email."""
        assert self.app.validate_email("invalid-email") == False
        assert self.app.validate_email("test@") == False
        assert self.app.validate_email("@domain.com") == False
        assert self.app.validate_email("") == False
    
    @patch('requests.post')
    def test_handle_login_success(self, mock_post):
        """Test successful login handling."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token",
            "user_id": "test_user",
            "email": "test@example.com"
        }
        mock_post.return_value = mock_response
        
        error_msg, status_msg, auth_data, tab_update = self.app.handle_login(
            "test@example.com", "password123"
        )
        
        assert error_msg == ""
        assert "Zalogowano pomyślnie" in status_msg
        assert auth_data["is_authenticated"] == True
        assert auth_data["user_id"] == "test_user"
        assert auth_data["email"] == "test@example.com"
    
    @patch('requests.post')
    def test_handle_login_failure(self, mock_post):
        """Test failed login handling."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid credentials"}
        mock_post.return_value = mock_response
        
        error_msg, status_msg, auth_data, tab_update = self.app.handle_login(
            "test@example.com", "wrongpassword"
        )
        
        assert "Nieprawidłowy email lub hasło" in error_msg
        assert auth_data is None
    
    @patch('requests.post')
    def test_handle_login_network_error(self, mock_post):
        """Test login handling with network error."""
        # Mock network error
        mock_post.side_effect = Exception("Connection failed")
        
        error_msg, status_msg, auth_data, tab_update = self.app.handle_login(
            "test@example.com", "password123"
        )
        
        assert "Błąd podczas logowania" in error_msg
        assert auth_data is None
    
    def test_handle_login_empty_inputs(self):
        """Test login handling with empty inputs."""
        error_msg, status_msg, auth_data, tab_update = self.app.handle_login("", "")
        
        assert "Email i hasło są wymagane" in error_msg
        assert auth_data is None
    
    def test_handle_login_invalid_email_format(self):
        """Test login handling with invalid email format."""
        error_msg, status_msg, auth_data, tab_update = self.app.handle_login(
            "invalid-email", "password123"
        )
        
        assert "Nieprawidłowy format adresu email" in error_msg
        assert auth_data is None
    
    @patch('requests.post')
    def test_handle_register_success(self, mock_post):
        """Test successful registration handling."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "access_token": "test_token",
            "user_id": "new_user",
            "email": "new@example.com"
        }
        mock_post.return_value = mock_response
        
        error_msg, status_msg, tab_update = self.app.handle_register(
            "new@example.com", "password123", "password123"
        )
        
        assert error_msg == ""
        assert "Konto zostało utworzone pomyślnie" in status_msg
    
    def test_handle_register_password_mismatch(self):
        """Test registration with password mismatch."""
        error_msg, status_msg, tab_update = self.app.handle_register(
            "test@example.com", "password123", "different123"
        )
        
        assert "Hasła nie są identyczne" in error_msg
    
    @patch('requests.post')
    def test_handle_register_failure(self, mock_post):
        """Test failed registration handling."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "User already exists"}
        mock_post.return_value = mock_response
        
        error_msg, status_msg, tab_update = self.app.handle_register(
            "existing@example.com", "password123", "password123"
        )
        
        assert "Błąd rejestracji" in error_msg
    
    @patch('requests.post')
    def test_handle_logout(self, mock_post):
        """Test logout handling."""
        # Set up authenticated state
        auth_state = {
            "is_authenticated": True,
            "user_id": "test_user",
            "email": "test@example.com",
            "token": "test_token"
        }
        
        # Mock successful logout response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        auth_data, tab_update = self.app.handle_logout(auth_state)
        
        assert auth_data is None

if __name__ == "__main__":
    pytest.main([__file__]) 