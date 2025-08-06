#!/usr/bin/env python3
"""
Launcher for the Unified Network Intrusion Detection System
Compliant with auth-spec.md requirements
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Launch the unified application with proper authentication flow."""
    try:
        from ui.unified_app import UnifiedApp
        
        # Get port from environment variable or use default
        server_port = int(os.getenv('GRADIO_SERVER_PORT', 7860))
        
        print("🚀 Uruchamianie zunifikowanego systemu detekcji intruzji...")
        print("📋 Implementacja zgodna z auth-spec.md")
        print("🔐 Wymagania autentykacji:")
        print("   - US-007: Użytkownik NIE MOŻE korzystać z funkcji bez logowania")
        print("   - Login tab jako domyślny")
        print("   - Analiza dostępna tylko po zalogowaniu")
        print("📡 Sprawdzanie połączenia z API...")
        
        # Create and launch the app
        unified_app = UnifiedApp()
        app = unified_app.create_app()
        
        print("✅ Aplikacja gotowa!")
        print(f"🌐 Otwórz przeglądarkę i przejdź do: http://localhost:{server_port}")
        print("🔐 Flow autentykacji:")
        print("   1. Start → Login tab (domyślny)")
        print("   2. Logowanie → FastAPI → Supabase Auth")
        print("   3. Sukces → JWT token → Analiza tab dostępny")
        print("   4. API calls → Wszystkie z tokenem w header")
        print("⏹️  Naciśnij Ctrl+C aby zatrzymać aplikację")
        
        app.launch(
            server_name="0.0.0.0",
            server_port=server_port,
            share=False,
            debug=True
        )
        
    except ImportError as e:
        print(f"❌ Błąd importu: {e}")
        print("💡 Upewnij się, że wszystkie zależności są zainstalowane:")
        print("   pip install gradio requests")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Błąd uruchamiania aplikacji: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 