import gradio as gr
import re
import logging
import requests
import json

logger = logging.getLogger(__name__)

class AuthLoginTab:
    def __init__(self):
        self.email = gr.Textbox(
            label="📧 Adres email",
            placeholder="twoj.email@example.com",
            type="email"
        )
        self.password = gr.Textbox(
            label="🔒 Hasło",
            placeholder="Wprowadź swoje hasło",
            type="password"
        )
        self.error_message = gr.Textbox(label="", visible=False, interactive=False)
        self.status_message = gr.Textbox(label="", visible=False, interactive=False)
        self.login_button = gr.Button("🔐 Zaloguj się", variant="primary")
        self.register_link = None
        self.api_base_url = "http://localhost:8000"
        
    def validate_email(self, email: str) -> bool:
        """Basic email validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_password(self, password: str) -> bool:
        """Password validation - minimum 8 characters."""
        return len(password) >= 8
    
    def handle_login(self, email, password):
        """Handle user login."""
        try:
            # Debug logging
            logger.info(f"Login attempt - email type: {type(email)}, password type: {type(password)}")
            logger.info(f"Login attempt - email value: {repr(email)}")
            logger.info(f"Login attempt - password value: {repr(password)}")
            
            # Check if email is a Gradio component
            if hasattr(email, '__class__') and 'gradio' in str(email.__class__).lower():
                logger.error(f"Email is a Gradio component: {email.__class__}")
                return "❌ Błąd: Nieprawidłowy typ danych email.", "", None
            
            # Input validation - ensure we have strings
            if not email or not isinstance(email, str):
                logger.error(f"Invalid email type: {type(email)}, value: {email}")
                return "❌ Adres email jest wymagany.", "", None
            
            email = email.strip()
            if not email:
                return "❌ Adres email jest wymagany.", "", None
            
            if not password or not isinstance(password, str):
                logger.error(f"Invalid password type: {type(password)}")
                return "", "❌ Hasło jest wymagane.", None
            
            password = password.strip()
            if not password:
                return "", "❌ Hasło jest wymagane.", None
            
            # Prepare login data
            login_data = {
                "email": email,
                "password": password
            }
            
            # Make API request
            response = requests.post(
                "http://localhost:8000/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                auth_data = {
                    "is_authenticated": True,
                    "user_id": result.get("user_id"),
                    "email": email,
                    "token": result.get("access_token"),
                    "username": result.get("username", email.split("@")[0])
                }
                logger.info(f"User {email} logged in successfully")
                return "", "✅ Zalogowano pomyślnie!", auth_data
            else:
                error_msg = response.json().get("detail", "Błąd logowania")
                logger.warning(f"Login failed for {email}: {error_msg}")
                return f"❌ {error_msg}", "", None
                
        except requests.exceptions.ConnectionError:
            error_msg = "❌ Nie można połączyć się z serwerem. Sprawdź, czy backend jest uruchomiony."
            logger.error("Connection error during login")
            return error_msg, "", None
        except Exception as e:
            error_msg = f"❌ Błąd podczas logowania: {str(e)}"
            logger.error(f"Login error: {str(e)}")
            return error_msg, "", None
    
    def go_to_register(self):
        """Navigate to registration tab."""
        return gr.update(selected=1)
    
    def go_to_forgot_password(self):
        """Navigate to forgot password tab."""
        return gr.update(selected=2)
    
    def render(self):
        """Render the login tab."""
        with gr.Column(elem_classes=["auth-container"]):
            with gr.Column(elem_classes=["login-form"]):
                gr.Markdown("## 🔐 Logowanie")
                gr.Markdown("Zaloguj się, aby uzyskać dostęp do systemu analizy ruchu.")
                
                # Use class attributes
                self.email
                self.password
                
                with gr.Row():
                    self.login_button
                    register_btn = gr.Button("📝 Rejestracja", variant="secondary")
                
                forgot_btn = gr.Button("🔑 Zapomniałeś hasła?", variant="secondary")
                
                # Error and status messages
                self.error_message
                self.status_message 