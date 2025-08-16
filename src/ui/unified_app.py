import json
import logging
import re
import uuid

import gradio as gr
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedApp:
    def __init__(self):
        self.api_base_url = "http://localhost:8000"
        self.auth_state = None

    def validate_email(self, email):
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def handle_login(self, email, password):
        """Handle user login according to auth-spec.md requirements."""
        try:
            # Input validation
            if not email or not password:
                return "❌ Email i hasło są wymagane.", "", None, gr.update(selected=0)

            if not self.validate_email(email):
                return (
                    "❌ Nieprawidłowy format adresu email.",
                    "",
                    None,
                    gr.update(selected=0),
                )

            # Prepare login data
            login_data = {"email": email.strip(), "password": password.strip()}

            # Make API request to FastAPI backend
            response = requests.post(
                f"{self.api_base_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                result = response.json()
                auth_data = {
                    "is_authenticated": True,
                    "user_id": result.get("user_id"),
                    "email": email,
                    "token": result.get("access_token"),
                    "username": email.split("@")[0],
                }
                logger.info(f"User {email} logged in successfully")

                # Return success and navigate to analysis tab (index 2)
                return (
                    "",
                    "✅ Zalogowano pomyślnie! Przekierowywanie do analizy...",
                    auth_data,
                    gr.update(selected=2),
                )
            else:
                # Handle error response
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", "Błąd logowania")

                    # Make error message more user-friendly
                    if (
                        "Invalid email or password" in error_msg
                        or "Invalid credentials" in error_msg
                    ):
                        error_msg = "❌ Nieprawidłowy email lub hasło. Sprawdź swoje dane i spróbuj ponownie."
                    elif "User not found" in error_msg:
                        error_msg = (
                            "❌ Użytkownik o podanym adresie email nie istnieje."
                        )
                    else:
                        error_msg = f"❌ {error_msg}"

                except:
                    error_msg = f"❌ Błąd logowania (status: {response.status_code})"

                logger.warning(f"Login failed for {email}: {error_msg}")
                logger.info(f"Returning error message: {error_msg}")
                return error_msg, "", None, gr.update(selected=0)

        except requests.exceptions.ConnectionError:
            error_msg = "❌ Nie można połączyć się z serwerem. Sprawdź, czy backend jest uruchomiony."
            logger.error("Connection error during login")
            return error_msg, "", None, gr.update(selected=0)
        except Exception as e:
            error_msg = f"❌ Błąd podczas logowania: {str(e)}"
            logger.error(f"Login error: {str(e)}")
            return error_msg, "", None, gr.update(selected=0)

    def handle_register(self, email, password, confirm_password):
        """Handle user registration according to auth-spec.md requirements."""
        try:
            # Input validation
            if not email or not password or not confirm_password:
                return "❌ Wszystkie pola są wymagane.", "", gr.update(selected=1)

            if not self.validate_email(email):
                return (
                    "❌ Nieprawidłowy format adresu email.",
                    "",
                    gr.update(selected=1),
                )

            if password != confirm_password:
                return "❌ Hasła nie są identyczne.", "", gr.update(selected=1)

            if len(password) < 8:
                return "❌ Hasło musi mieć minimum 8 znaków.", "", gr.update(selected=1)

            # Prepare registration data
            register_data = {
                "email": email.strip(),
                "password": password.strip(),
                "confirm_password": confirm_password.strip(),
            }

            # Make API request to FastAPI backend
            response = requests.post(
                f"{self.api_base_url}/auth/register",
                json=register_data,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 201:
                result = response.json()
                status_msg = f"✅ Konto zostało utworzone pomyślnie dla {result['email']}. Możesz się teraz zalogować."
                logger.info(f"User registered successfully: {email}")
                return "", status_msg, gr.update(selected=0)  # Navigate to login tab
            else:
                error_data = response.json()
                error_msg = (
                    f"❌ Błąd rejestracji: {error_data.get('detail', 'Nieznany błąd')}"
                )
                logger.error(f"Registration failed for {email}: {error_msg}")
                return error_msg, "", gr.update(selected=1)

        except requests.exceptions.ConnectionError:
            error_msg = "❌ Nie można połączyć się z serwerem. Sprawdź czy API jest uruchomione."
            return error_msg, "", gr.update(selected=1)
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            return (
                f"❌ Wystąpił błąd podczas rejestracji: {str(e)}",
                "",
                gr.update(selected=1),
            )

    def handle_logout(self, auth_state):
        """Handle logout according to auth-spec.md requirements."""
        try:
            if auth_state and auth_state.get("is_authenticated"):
                # Call logout API
                headers = {"Authorization": f"Bearer {auth_state['token']}"}

                response = requests.post(
                    f"{self.api_base_url}/auth/logout", headers=headers
                )
                logger.info("User logged out successfully")

            # Return to login state and navigate to login tab
            return None, gr.update(selected=0)

        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            return None, gr.update(selected=0)

    def handle_logout_with_ui_reset(self, auth_state):
        """Handle logout with complete UI reset."""
        try:
            if auth_state and auth_state.get("is_authenticated"):
                # Call logout API
                headers = {"Authorization": f"Bearer {auth_state['token']}"}

                response = requests.post(
                    f"{self.api_base_url}/auth/logout", headers=headers
                )
                logger.info("User logged out successfully")

            # Return to login state and navigate to login tab
            # Also reset all user-related components
            return (
                None,  # auth_state
                gr.update(selected=0),  # tabs
                "👤 Zalogowany jako: Nie zalogowany",  # user_info
                "",  # login_email (clear email field)
                "",  # login_password (clear password field)
                "",  # login_error (clear error messages)
                "",  # login_status (clear status messages)
                "",  # output (clear analysis results)
            )

        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            return (
                None,  # auth_state
                gr.update(selected=0),  # tabs
                "👤 Zalogowany jako: Nie zalogowany",  # user_info
                "",  # login_email
                "",  # login_password
                "",  # login_error
                "",  # login_status
                "",  # output
            )

    def classify_traffic(
        self,
        logged_in,
        count,
        serror_rate,
        srv_serror_rate,
        same_srv_rate,
        dst_host_srv_count,
        dst_host_same_srv_rate,
        dst_host_serror_rate,
        dst_host_srv_serror_rate,
        flag,
        auth_state,
    ):
        """Classify traffic with authentication - US-007 requirement."""
        try:
            # US-007: User CANNOT use application functions without logging in
            if not auth_state or not auth_state.get("is_authenticated"):
                return "❌ Musisz być zalogowany, aby korzystać z tej funkcji. Przejdź do zakładki 'Logowanie'."

            # Prepare the request data in the correct format for the API
            traffic_data = {
                "features": {
                    "logged_in": logged_in,
                    "count": int(count),
                    "serror_rate": float(serror_rate),
                    "srv_serror_rate": float(srv_serror_rate),
                    "same_srv_rate": float(same_srv_rate),
                    "dst_host_srv_count": int(dst_host_srv_count),
                    "dst_host_same_srv_rate": float(dst_host_same_srv_rate),
                    "dst_host_serror_rate": float(dst_host_serror_rate),
                    "dst_host_srv_serror_rate": float(dst_host_srv_serror_rate),
                    "flag": flag,
                },
                "correlation_id": str(uuid.uuid4()),
                "model_version": "4",
            }

            # Make request to authenticated API with JWT token
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_state['token']}",
            }

            response = requests.post(
                f"{self.api_base_url}/decisions/single",
                json=traffic_data,
                headers=headers,
            )

            if response.status_code == 200:
                result = response.json()
                return f"✅ Classification: {result['classification_result']}\nTimestamp: {result['timestamp']}\nCorrelation ID: {result['correlation_id']}"
            elif response.status_code == 401:
                return "❌ Sesja wygasła. Zaloguj się ponownie."
            else:
                return f"❌ Error: {response.status_code} - {response.text}"

        except Exception as e:
            return f"❌ Error: {str(e)}"

    def create_app(self):
        """Create the unified Gradio interface according to auth-spec.md."""

        # Custom CSS for better styling
        custom_css = """
        .auth-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .login-form, .register-form {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .error-message {
            color: #dc3545;
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            font-weight: bold;
        }
        
        .status-message {
            color: #155724;
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            font-weight: bold;
        }
        
        .login-error, .register-error {
            color: #dc3545 !important;
            background: #f8d7da !important;
            border: 3px solid #f5c6cb !important;
            border-radius: 8px !important;
            padding: 15px !important;
            margin: 15px 0 !important;
            font-weight: bold !important;
            font-size: 16px !important;
            text-align: center !important;
            box-shadow: 0 2px 4px rgba(220, 53, 69, 0.2) !important;
        }
        
        .login-status, .register-status {
            color: #155724 !important;
            background: #d4edda !important;
            border: 3px solid #c3e6cb !important;
            border-radius: 8px !important;
            padding: 15px !important;
            margin: 15px 0 !important;
            font-weight: bold !important;
            font-size: 16px !important;
            text-align: center !important;
            box-shadow: 0 2px 4px rgba(21, 87, 36, 0.2) !important;
        }
        
        .logout-container {
            justify-content: space-between;
            align-items: center;
            padding: 10px 20px;
            background: #e9ecef;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .analysis-container {
            background: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .protected-content {
            border: 2px solid #28a745;
            border-radius: 10px;
            padding: 20px;
            background: #f8fff9;
        }
        """

        with gr.Blocks(
            title="🛡️ Detektor Ruchu Złośliwego - System z Autentykacją",
            theme=gr.themes.Soft(),
            css=custom_css,
        ) as app:

            # Authentication state
            auth_state = gr.State(value=None)

            # Main header
            gr.Markdown("# 🛡️ Detektor Ruchu Złośliwego")
            gr.Markdown(
                "### System analizy ruchu sieciowego z autentykacją użytkowników"
            )

            # Main tabs - Login tab is default (index 0) according to auth-spec.md
            with gr.Tabs(selected=0) as tabs:

                # Login tab (default) - index 0
                with gr.Tab("🔐 Logowanie", id=0):
                    with gr.Column(elem_classes=["auth-container"]):
                        with gr.Column(elem_classes=["login-form"]):
                            gr.Markdown("## 🔐 Logowanie")
                            gr.Markdown(
                                "**Zaloguj się, aby uzyskać dostęp do systemu analizy ruchu.**"
                            )
                            gr.Markdown(
                                "*Wymagane: Użytkownik NIE MOŻE korzystać z funkcji aplikacji bez logowania (US-007)*"
                            )

                            login_email = gr.Textbox(
                                label="📧 Adres email",
                                placeholder="twoj.email@example.com",
                                type="email",
                            )
                            login_password = gr.Textbox(
                                label="🔒 Hasło",
                                placeholder="Wprowadź swoje hasło",
                                type="password",
                            )
                            login_error = gr.Textbox(
                                label="",
                                visible=True,
                                interactive=False,
                                elem_classes=["login-error"],
                            )
                            login_status = gr.Textbox(
                                label="",
                                visible=True,
                                interactive=False,
                                elem_classes=["login-status"],
                            )
                            login_button = gr.Button(
                                "🔐 Zaloguj się", variant="primary"
                            )

                            # Link to registration
                            gr.Markdown("---")
                            gr.Markdown(
                                "**Nie masz konta?** [Przejdź do zakładki Rejestracja](#)"
                            )

                # Registration tab - index 1
                with gr.Tab("📝 Rejestracja", id=1):
                    with gr.Column(elem_classes=["auth-container"]):
                        with gr.Column(elem_classes=["register-form"]):
                            gr.Markdown("## 📝 Rejestracja nowego konta")
                            gr.Markdown(
                                "**Utwórz nowe konto, aby uzyskać dostęp do systemu.**"
                            )
                            gr.Markdown(
                                "*Hasło musi mieć minimum 8 znaków zgodnie z wymaganiami Supabase*"
                            )

                            register_email = gr.Textbox(
                                label="📧 Adres email",
                                placeholder="twoj.email@example.com",
                                type="email",
                            )
                            register_password = gr.Textbox(
                                label="🔒 Hasło",
                                placeholder="Minimum 8 znaków",
                                type="password",
                            )
                            register_confirm = gr.Textbox(
                                label="🔒 Potwierdź hasło",
                                placeholder="Powtórz hasło",
                                type="password",
                            )
                            register_error = gr.Textbox(
                                label="",
                                visible=True,
                                interactive=False,
                                elem_classes=["register-error"],
                            )
                            register_status = gr.Textbox(
                                label="",
                                visible=True,
                                interactive=False,
                                elem_classes=["register-status"],
                            )
                            register_button = gr.Button(
                                "📝 Zarejestruj się", variant="primary"
                            )

                            # Link to login
                            gr.Markdown("---")
                            gr.Markdown(
                                "**Masz już konto?** [Przejdź do zakładki Logowanie](#)"
                            )

                # Analysis tab (protected) - index 2
                with gr.Tab("🔍 Analiza ruchu", id=2):
                    # Logout section
                    with gr.Row(elem_classes=["logout-container"]):
                        user_info = gr.Markdown(
                            "👤 Zalogowany jako: Nie zalogowany",
                            elem_classes=["user-info"],
                        )
                        logout_button = gr.Button(
                            "🚪 Wyloguj się",
                            variant="secondary",
                            elem_classes=["logout-button"],
                        )

                    # Protected content - only visible after authentication
                    with gr.Column(
                        elem_classes=["analysis-container", "protected-content"]
                    ):
                        gr.Markdown("## 🔍 Analiza ruchu sieciowego")
                        gr.Markdown(
                            "**Wprowadź parametry ruchu sieciowego, aby wykryć potencjalne zagrożenia.**"
                        )
                        gr.Markdown("*Dostępne tylko dla zalogowanych użytkowników*")

                        with gr.Row():
                            with gr.Column(scale=1):
                                gr.Markdown("### 📊 Parametry ruchu")

                                logged_in = gr.Checkbox(label="Zalogowany", value=True)
                                count = gr.Number(
                                    label="Liczba połączeń", value=45, minimum=0
                                )
                                serror_rate = gr.Slider(
                                    label="Współczynnik błędów SYN",
                                    value=0.05,
                                    minimum=0,
                                    maximum=1,
                                    step=0.01,
                                )
                                srv_serror_rate = gr.Slider(
                                    label="Współczynnik błędów SYN serwisu",
                                    value=0.04,
                                    minimum=0,
                                    maximum=1,
                                    step=0.01,
                                )
                                same_srv_rate = gr.Slider(
                                    label="Współczynnik tego samego serwisu",
                                    value=0.88,
                                    minimum=0,
                                    maximum=1,
                                    step=0.01,
                                )

                            with gr.Column(scale=1):
                                gr.Markdown("### 🌐 Parametry hosta docelowego")

                                dst_host_srv_count = gr.Number(
                                    label="Liczba serwisów hosta docelowego",
                                    value=110,
                                    minimum=0,
                                )
                                dst_host_same_srv_rate = gr.Slider(
                                    label="Współczynnik tego samego serwisu hosta docelowego",
                                    value=0.99,
                                    minimum=0,
                                    maximum=1,
                                    step=0.01,
                                )
                                dst_host_serror_rate = gr.Slider(
                                    label="Współczynnik błędów SYN hosta docelowego",
                                    value=0.02,
                                    minimum=0,
                                    maximum=1,
                                    step=0.01,
                                )
                                dst_host_srv_serror_rate = gr.Slider(
                                    label="Współczynnik błędów SYN serwisu hosta docelowego",
                                    value=0.01,
                                    minimum=0,
                                    maximum=1,
                                    step=0.01,
                                )
                                flag = gr.Dropdown(
                                    label="Flaga", choices=["S0", "SF"], value="S0"
                                )

                        with gr.Row():
                            analyze_btn = gr.Button(
                                "🔍 Analizuj ruch", variant="primary", size="lg"
                            )

                        with gr.Row():
                            output = gr.Textbox(
                                label="Wynik analizy", lines=5, interactive=False
                            )

                        # Sample data buttons
                        with gr.Row():
                            gr.Markdown("### 📋 Przykładowe dane")

                        with gr.Row():
                            normal_btn = gr.Button(
                                "Wczytaj normalny ruch", variant="secondary"
                            )
                            malicious_btn = gr.Button(
                                "Wczytaj złośliwy ruch", variant="secondary"
                            )

            # Information section
            with gr.Accordion("ℹ️ Informacje o systemie", open=False):
                gr.Markdown(
                    """
                **Detektor Ruchu Złośliwego z Autentykacją (zgodnie z auth-spec.md)**
                
                Ten system implementuje wymagania US-007: Użytkownik NIE MOŻE korzystać z funkcji aplikacji bez logowania.
                
                **Funkcje autentykacji (Supabase):**
                - 🔐 Bezpieczne logowanie z adresem email i hasłem
                - 📝 Rejestracja nowych kont użytkowników (min. 8 znaków)
                - 🚪 Wylogowanie z systemu
                - 🛡️ Ochrona przed nieautoryzowanym dostępem
                - 🔒 JWT tokens dla bezpiecznych sesji
                
                **Funkcje analizy (tylko dla zalogowanych):**
                - 🔍 Klasyfikacja pojedynczych zdarzeń sieciowych
                - 📊 Analiza parametrów ruchu w czasie rzeczywistym
                - 🛡️ Wykrywanie złośliwego ruchu sieciowego
                - 📋 Przykładowe dane do testowania
                
                **Architektura:**
                - **Model ML:** Logistic Regression (F1 Score: 0.7332)
                - **API:** FastAPI z autentykacją Supabase
                - **Interfejs:** Gradio z responsywnym designem
                - **Baza danych:** PostgreSQL z Row Level Security
                
                **Flow autentykacji:**
                1. Start aplikacji → Login tab (domyślny)
                2. Logowanie → FastAPI → Supabase Auth
                3. Sukces → JWT token → Analiza tab dostępny
                4. API calls → Wszystkie z tokenem w header
                """
                )

            # Event handlers according to auth-spec.md

            # Connect login with proper navigation
            login_button.click(
                fn=self.handle_login,
                inputs=[login_email, login_password],
                outputs=[login_error, login_status, auth_state, tabs],
            )

            # Connect registration with navigation to login
            register_button.click(
                fn=self.handle_register,
                inputs=[register_email, register_password, register_confirm],
                outputs=[register_error, register_status, tabs],
            )

            # Connect logout with navigation to login
            logout_button.click(
                fn=self.handle_logout_with_ui_reset,
                inputs=[auth_state],
                outputs=[
                    auth_state,
                    tabs,
                    user_info,
                    login_email,
                    login_password,
                    login_error,
                    login_status,
                    output,
                ],
            )

            # Connect traffic analysis (protected)
            analyze_btn.click(
                fn=self.classify_traffic,
                inputs=[
                    logged_in,
                    count,
                    serror_rate,
                    srv_serror_rate,
                    same_srv_rate,
                    dst_host_srv_count,
                    dst_host_same_srv_rate,
                    dst_host_serror_rate,
                    dst_host_srv_serror_rate,
                    flag,
                    auth_state,
                ],
                outputs=output,
            )

            # Sample data functions
            def load_normal_sample():
                return [True, 45, 0.05, 0.04, 0.88, 110, 0.99, 0.02, 0.01, "S0"]

            def load_malicious_sample():
                return [False, 100, 0.8, 0.9, 0.1, 5, 0.1, 0.9, 0.8, "SF"]

            normal_btn.click(
                fn=load_normal_sample,
                outputs=[
                    logged_in,
                    count,
                    serror_rate,
                    srv_serror_rate,
                    same_srv_rate,
                    dst_host_srv_count,
                    dst_host_same_srv_rate,
                    dst_host_serror_rate,
                    dst_host_srv_serror_rate,
                    flag,
                ],
            )

            malicious_btn.click(
                fn=load_malicious_sample,
                outputs=[
                    logged_in,
                    count,
                    serror_rate,
                    srv_serror_rate,
                    same_srv_rate,
                    dst_host_srv_count,
                    dst_host_same_srv_rate,
                    dst_host_serror_rate,
                    dst_host_srv_serror_rate,
                    flag,
                ],
            )

        return app


if __name__ == "__main__":
    unified_app = UnifiedApp()
    app = unified_app.create_app()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, debug=True)
