# 🛡️ Detektor Ruchu Złośliwego - System Zunifikowany

## 📋 Przegląd

Zunifikowany system detekcji intruzji sieciowych łączy zaawansowaną analizę ruchu sieciowego z bezpieczną autentykacją użytkowników. System wykorzystuje uczenie maszynowe do wykrywania złośliwego ruchu w czasie rzeczywistym.

## ✨ Funkcje

### 🔐 Autentykacja
- **Bezpieczne logowanie** z adresem email i hasłem
- **Rejestracja nowych kont** użytkowników
- **Wylogowanie** z systemu
- **Ochrona przed nieautoryzowanym dostępem**

### 🔍 Analiza ruchu
- **Klasyfikacja pojedynczych zdarzeń** sieciowych
- **Analiza parametrów ruchu** w czasie rzeczywistym
- **Wykrywanie złośliwego ruchu** sieciowego
- **Przykładowe dane** do testowania

## 🏗️ Architektura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gradio UI     │    │   FastAPI       │    │   Supabase      │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Database)    │
│   Port: 7860    │    │   Port: 8000    │    │   (Auth/Data)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Komponenty
- **Frontend**: Gradio z responsywnym interfejsem
- **Backend**: FastAPI z autentykacją JWT
- **Database**: Supabase (PostgreSQL + Auth)
- **ML Model**: Logistic Regression (F1 Score: 0.7332)

## 🚀 Szybki start

### 1. Uruchomienie backendu
```bash
# Terminal 1 - Backend API
cd /home/mariusz/Desktop/Intrusion-detector
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Uruchomienie frontendu
```bash
# Terminal 2 - Unified Frontend
cd /home/mariusz/Desktop/Intrusion-detector
source venv/bin/activate
python run_unified_app.py
```

### 3. Dostęp do aplikacji
- **Frontend**: http://localhost:7860
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📱 Interfejs użytkownika

### 🔐 Zakładka Logowania
- Formularz logowania z walidacją
- Obsługa błędów połączenia
- Automatyczne przekierowanie po zalogowaniu

### 📝 Zakładka Rejestracji
- Formularz rejestracji z walidacją hasła
- Sprawdzanie zgodności haseł
- Komunikaty o statusie rejestracji

### 🔍 Zakładka Analizy (Chroniona)
- **Parametry ruchu**:
  - Liczba połączeń
  - Współczynniki błędów SYN
  - Współczynniki serwisów
- **Parametry hosta docelowego**:
  - Liczba serwisów
  - Współczynniki błędów
  - Flagi połączeń
- **Przykładowe dane**:
  - Normalny ruch sieciowy
  - Złośliwy ruch sieciowy

## 🔧 Konfiguracja

### Zmienne środowiskowe
```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=7860
```

### Zależności
```bash
# Backend dependencies
fastapi==0.104.1
uvicorn==0.24.0
supabase==2.0.2
python-jose==3.3.0
passlib==1.7.4
python-multipart==0.0.6
scikit-learn==1.3.2
pandas==2.1.4
numpy==1.25.2

# Frontend dependencies
gradio==4.15.0
requests==2.31.0
```

## 🔒 Bezpieczeństwo

### Autentykacja
- **JWT Tokens**: Bezpieczne tokeny sesji
- **Password Hashing**: bcrypt dla haseł
- **Input Validation**: Walidacja wszystkich danych wejściowych
- **CORS Protection**: Konfiguracja CORS dla bezpieczeństwa

### Autoryzacja
- **Protected Endpoints**: Wszystkie endpointy analizy wymagają autentykacji
- **Token Validation**: Sprawdzanie ważności tokenów
- **User Sessions**: Zarządzanie sesjami użytkowników

## 📊 Model ML

### Algorytm
- **Logistic Regression** z optymalizacją hiperparametrów
- **F1 Score**: 0.7332
- **Accuracy**: Wysoka dokładność klasyfikacji

### Features
- `logged_in`: Status logowania
- `count`: Liczba połączeń
- `serror_rate`: Współczynnik błędów SYN
- `srv_serror_rate`: Współczynnik błędów SYN serwisu
- `same_srv_rate`: Współczynnik tego samego serwisu
- `dst_host_srv_count`: Liczba serwisów hosta docelowego
- `dst_host_same_srv_rate`: Współczynnik tego samego serwisu hosta docelowego
- `dst_host_serror_rate`: Współczynnik błędów SYN hosta docelowego
- `dst_host_srv_serror_rate`: Współczynnik błędów SYN serwisu hosta docelowego
- `flag`: Flaga połączenia

## 🧪 Testowanie

### Przykładowe dane
```python
# Normalny ruch
normal_traffic = {
    "logged_in": True,
    "count": 45,
    "serror_rate": 0.05,
    "srv_serror_rate": 0.04,
    "same_srv_rate": 0.88,
    "dst_host_srv_count": 110,
    "dst_host_same_srv_rate": 0.99,
    "dst_host_serror_rate": 0.02,
    "dst_host_srv_serror_rate": 0.01,
    "flag": "S0"
}

# Złośliwy ruch
malicious_traffic = {
    "logged_in": False,
    "count": 100,
    "serror_rate": 0.8,
    "srv_serror_rate": 0.9,
    "same_srv_rate": 0.1,
    "dst_host_srv_count": 5,
    "dst_host_same_srv_rate": 0.1,
    "dst_host_serror_rate": 0.9,
    "dst_host_srv_serror_rate": 0.8,
    "flag": "SF"
}
```

## 🐛 Rozwiązywanie problemów

### Częste problemy

#### 1. Błąd połączenia z API
```
❌ Nie można połączyć się z serwerem. Sprawdź, czy backend jest uruchomiony.
```
**Rozwiązanie**: Upewnij się, że backend API jest uruchomiony na porcie 8000.

#### 2. Błąd autentykacji
```
❌ Błąd logowania: Invalid credentials
```
**Rozwiązanie**: Sprawdź poprawność adresu email i hasła.

#### 3. Błąd Gradio
```
AttributeError: module 'gradio' has no attribute 'Box'
```
**Rozwiązanie**: Zaktualizuj Gradio do najnowszej wersji: `pip install --upgrade gradio`

### Logi
- **Backend**: Sprawdź logi w terminalu z uvicorn
- **Frontend**: Sprawdź logi w terminalu z Gradio
- **Browser**: Sprawdź konsolę deweloperską (F12)

## 📈 Rozwój

### Struktura plików
```
Intrusion-detector/
├── src/
│   ├── main.py                 # FastAPI backend
│   ├── auth/                   # Autentykacja
│   ├── ml/                     # Model ML
│   ├── models/                 # Modele danych
│   └── ui/
│       └── unified_app.py      # Zunifikowany frontend
├── run_unified_app.py          # Launcher
├── requirements.txt            # Zależności
└── README_UNIFIED.md          # Dokumentacja
```

### Dodawanie nowych funkcji
1. Dodaj endpoint w `src/main.py`
2. Zaktualizuj interfejs w `src/ui/unified_app.py`
3. Przetestuj funkcjonalność
4. Zaktualizuj dokumentację

## 📞 Wsparcie

### Kontakt
- **Email**: support@intrusion-detector.com
- **GitHub**: https://github.com/your-repo/intrusion-detector
- **Documentation**: http://localhost:8000/docs

### Status
- ✅ Backend API: Działa
- ✅ Frontend UI: Działa
- ✅ Autentykacja: Działa
- ✅ Model ML: Działa
- ✅ Database: Działa

---

**Wersja**: 2.0.0  
**Ostatnia aktualizacja**: 2024-01-XX  
**Autor**: System Detekcji Intruzji 