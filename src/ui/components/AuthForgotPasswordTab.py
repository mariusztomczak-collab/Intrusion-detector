import gradio as gr
import re
import logging
import requests
import json

logger = logging.getLogger(__name__)

class AuthForgotPasswordTab:
    def __init__(self):
        self.email_input = None
        self.reset_button = None
        self.back_to_login_link = None
        self.error_message = None
        self.status_message = None
        self.api_base_url = "http://localhost:8000"
        
    def validate_email(self, email: str) -> bool:
        """Basic email validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def handle_password_reset(self, email: str):
        """Handle password reset request with backend integration."""
        try:
            # Clear previous messages
            error_msg = ""
            status_msg = ""
            
            # Validate inputs
            if not email:
                error_msg = "Adres email jest wymagany."
                return error_msg, status_msg
            
            if not self.validate_email(email):
                error_msg = "Nieprawidłowy format adresu email."
                return error_msg, status_msg
            
            # Call password reset API
            reset_data = {
                "email": email
            }
            
            response = requests.post(
                f"{self.api_base_url}/auth/forgot-password",
                json=reset_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                status_msg = f"Link do resetowania hasła został wysłany na adres {email}."
                logger.info(f"Password reset email sent to: {email}")
                return error_msg, status_msg
            else:
                error_data = response.json()
                error_msg = f"Błąd resetowania hasła: {error_data.get('detail', 'Nieznany błąd')}"
                logger.error(f"Password reset failed for {email}: {error_msg}")
                return error_msg, status_msg
            
        except requests.exceptions.ConnectionError:
            error_msg = "Nie można połączyć się z serwerem. Sprawdź czy API jest uruchomione."
            return error_msg, status_msg
        except Exception as e:
            logger.error(f"Error during password reset: {str(e)}")
            return f"Wystąpił błąd podczas resetowania hasła: {str(e)}", ""
    
    def go_to_login(self):
        """Navigate to login tab."""
        return gr.update(selected=0)
    
    def render(self):
        """Render the forgot password interface."""
        with gr.Column(elem_classes=["auth-container"]):
            # Header
            gr.Markdown("## 🔑 Resetowanie hasła")
            gr.Markdown("Wprowadź swój adres email, aby otrzymać link do resetowania hasła.")
            
            # Password reset form
            with gr.Column(elem_classes=["forgot-password-form"]):
                self.email_input = gr.Textbox(
                    label="Adres email",
                    placeholder="twoj.email@example.com",
                    type="email",
                    elem_classes=["email-input"]
                )
                
                self.reset_button = gr.Button(
                    "Wyślij link resetowania",
                    variant="primary",
                    size="lg",
                    elem_classes=["reset-button"]
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
                    gr.Markdown("Pamiętasz hasło?")
                    self.back_to_login_link = gr.Button(
                        "Wróć do logowania",
                        variant="secondary",
                        size="sm",
                        elem_classes=["back-to-login-link"]
                    )
            
            # Event handlers
            self.reset_button.click(
                fn=self.handle_password_reset,
                inputs=[self.email_input],
                outputs=[self.error_message, self.status_message]
            )
            
            self.back_to_login_link.click(
                fn=self.go_to_login,
                outputs=gr.State()
            ) 