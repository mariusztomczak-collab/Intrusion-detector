import gradio as gr
import re
import logging
import requests
import json

logger = logging.getLogger(__name__)

class AuthRegisterTab:
    def __init__(self):
        self.email_input = None
        self.password_input = None
        self.confirm_password_input = None
        self.register_button = None
        self.login_link = None
        self.error_message = None
        self.status_message = None
        self.api_base_url = "http://localhost:8000"
        
    def validate_email(self, email: str) -> bool:
        """Basic email validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_password(self, password: str) -> bool:
        """Password validation - minimum 8 characters."""
        return len(password) >= 8
    
    def validate_password_match(self, password: str, confirm_password: str) -> bool:
        """Check if passwords match."""
        return password == confirm_password
    
    def handle_register(self, email: str, password: str, confirm_password: str):
        """Handle registration attempt with backend integration."""
        try:
            # Clear previous messages
            error_msg = ""
            status_msg = ""
            
            # Validate inputs
            if not email or not password or not confirm_password:
                error_msg = "Wszystkie pola są wymagane."
                return error_msg, status_msg
            
            if not self.validate_email(email):
                error_msg = "Nieprawidłowy format adresu email."
                return error_msg, status_msg
            
            if not self.validate_password(password):
                error_msg = "Hasło musi mieć minimum 8 znaków."
                return error_msg, status_msg
            
            if not self.validate_password_match(password, confirm_password):
                error_msg = "Hasła nie są identyczne."
                return error_msg, status_msg
            
            # Call registration API
            register_data = {
                "email": email,
                "password": password,
                "confirm_password": confirm_password
            }
            
            response = requests.post(
                f"{self.api_base_url}/auth/register",
                json=register_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                auth_data = response.json()
                status_msg = f"Konto zostało utworzone pomyślnie dla {auth_data['email']}. Możesz się teraz zalogować."
                logger.info(f"User registered successfully: {email}")
                return error_msg, status_msg
            else:
                error_data = response.json()
                error_msg = f"Błąd rejestracji: {error_data.get('detail', 'Nieznany błąd')}"
                logger.error(f"Registration failed for {email}: {error_msg}")
                return error_msg, status_msg
            
        except requests.exceptions.ConnectionError:
            error_msg = "Nie można połączyć się z serwerem. Sprawdź czy API jest uruchomione."
            return error_msg, status_msg
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            return f"Wystąpił błąd podczas rejestracji: {str(e)}", ""
    
    def go_to_login(self):
        """Navigate to login tab."""
        return gr.update(selected=0)
    
    def render(self):
        """Render the register interface."""
        with gr.Column(elem_classes=["auth-container"]):
            # Header
            gr.Markdown("## 📝 Rejestracja nowego konta")
            gr.Markdown("Utwórz nowe konto, aby uzyskać dostęp do systemu.")
            
            # Register form
            with gr.Column(elem_classes=["register-form"]):
                self.email_input = gr.Textbox(
                    label="Adres email",
                    placeholder="twoj.email@example.com",
                    type="email",
                    elem_classes=["email-input"]
                )
                
                self.password_input = gr.Textbox(
                    label="Hasło",
                    placeholder="Minimum 8 znaków",
                    type="password",
                    elem_classes=["password-input"]
                )
                
                self.confirm_password_input = gr.Textbox(
                    label="Potwierdź hasło",
                    placeholder="Powtórz hasło",
                    type="password",
                    elem_classes=["confirm-password-input"]
                )
                
                self.register_button = gr.Button(
                    "Zarejestruj się",
                    variant="primary",
                    size="lg",
                    elem_classes=["register-button"]
                )
                
                # Error and status messages
                self.error_message = gr.Textbox(
                    label="",
                    value="",
                    interactive=False,
                    visible=False,
                    elem_classes=["error-message"]
                )
                
                self.status_message = gr.Textbox(
                    label="",
                    value="",
                    interactive=False,
                    visible=False,
                    elem_classes=["status-message"]
                )
                
                # Navigation
                with gr.Row():
                    gr.Markdown("Masz już konto?")
                    self.login_link = gr.Button(
                        "Zaloguj się",
                        variant="secondary",
                        size="sm",
                        elem_classes=["login-link"]
                    )
            
            # Event handlers
            self.register_button.click(
                fn=self.handle_register,
                inputs=[self.email_input, self.password_input, self.confirm_password_input],
                outputs=[self.error_message, self.status_message]
            )
            
            # Remove the problematic navigation handler for now
            # self.login_link.click(
            #     fn=self.go_to_login,
            #     outputs=gr.State()
            # ) 