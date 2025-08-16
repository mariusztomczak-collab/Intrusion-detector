from unittest.mock import Mock, patch

import pytest

from src.ui.unified_app import UnifiedApp


class TestUnifiedApp:
    """Unit tests for UnifiedApp class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.app = UnifiedApp()
        self.app.api_base_url = "http://localhost:8000"
    
    def test_validate_email_valid(self):
        """Test email validation with valid emails"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        for email in valid_emails:
            assert self.app.validate_email(email) == True
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid emails"""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user.example.com",
            ""
        ]
        
        for email in invalid_emails:
            assert self.app.validate_email(email) == False
    
    @patch('requests.post')
    def test_handle_login_success(self, mock_post):
        """Test successful login"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user_id": "123",
            "access_token": "jwt_token_here"
        }
        mock_post.return_value = mock_response
        
        # Test login
        error_msg, status_msg, auth_data, tab_update = self.app.handle_login(
            "test@example.com", "password123"
        )
        
        # Assertions
        assert error_msg == ""
        assert "Zalogowano pomyślnie" in status_msg
        assert auth_data["is_authenticated"] == True
        assert auth_data["email"] == "test@example.com"
    
    @patch('requests.post')
    def test_handle_login_invalid_credentials(self, mock_post):
        """Test login with invalid credentials"""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "detail": "Invalid email or password"
        }
        mock_post.return_value = mock_response
        
        # Test login
        error_msg, status_msg, auth_data, tab_update = self.app.handle_login(
            "test@example.com", "wrongpassword"
        )
        
        # Assertions
        assert "Nieprawidłowy email lub hasło" in error_msg
        assert status_msg == ""
        assert auth_data is None
    
    def test_handle_login_empty_inputs(self):
        """Test login with empty inputs"""
        error_msg, status_msg, auth_data, tab_update = self.app.handle_login("", "")
        
        assert "Email i hasło są wymagane" in error_msg
        assert auth_data is None
    
    def test_handle_login_invalid_email_format(self):
        """Test login with invalid email format"""
        error_msg, status_msg, auth_data, tab_update = self.app.handle_login(
            "invalid-email", "password123"
        )
        
        assert "Nieprawidłowy format adresu email" in error_msg
        assert auth_data is None

class TestAuthAPI:
    """Unit tests for auth API functions"""
    
    def test_validate_email_function(self):
        """Test standalone email validation function"""
        app = UnifiedApp()
        assert app.validate_email("test@example.com") == True
        assert app.validate_email("invalid-email") == False
        assert app.validate_email("") == False
    
    @patch('requests.post')
    def test_handle_login_api_error(self, mock_post):
        """Test login API error handling"""
        # Mock connection error
        mock_post.side_effect = Exception("Connection failed")
        
        app = UnifiedApp()
        error_msg, status_msg, auth_data, tab_update = app.handle_login(
            "test@example.com", "password123"
        )
        
        assert "Błąd podczas logowania" in error_msg
        assert auth_data is None

if __name__ == "__main__":
    pytest.main([__file__]) 