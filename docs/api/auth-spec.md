# Specyfikacja Autentykacji - Detektor Ruchu Złośliwego (MVP z Supabase)

## 1. ZAŁOŻENIA MVP ZGODNE Z PRD

### 1.1 Ograniczenia MVP
- **Minimalistyczny UI**: Interfejs oparty na Gradio, nie tradycyjny web UI
- **Lokalne przechowywanie**: Historia zapytań zapisywana lokalnie
- **Supabase lokalny**: Używamy lokalnej instancji Supabase (docker-compose)
- **Offline-first**: Supabase działa lokalnie, nie wymaga internetu

### 1.2 Wymagania autentykacji
- **US-007**: Użytkownik NIE MOŻE korzystać z funkcji aplikacji bez logowania
- **Supabase Auth**: Wykorzystanie Supabase jako systemu autentykacji
- **Gradio Integration**: Integracja z interfejsem Gradio
- **Lokalne działanie**: Supabase uruchamiany lokalnie przez Docker

## 2. ARCHITEKTURA AUTENTYKACJI (SUPABASE)

### 2.1 Lokalny Supabase
- **Docker Compose**: Supabase uruchamiany lokalnie
- **Baza danych**: PostgreSQL (lokalny)
- **Auth**: Supabase Auth z JWT tokens
- **API**: Supabase REST API lokalnie

### 2.2 Struktura bazy danych (Supabase)
```sql
-- Tabela użytkowników (zarządzana przez Supabase Auth)
-- auth.users - automatycznie tworzona przez Supabase

-- Tabela decyzji (custom)
CREATE TABLE decisions (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    correlation_id TEXT,
    source_type TEXT,
    batch_filename TEXT,
    batch_file_contents TEXT,
    model_version TEXT,
    classification_result TEXT,
    logged_in BOOLEAN,
    count INTEGER,
    serror_rate DOUBLE PRECISION,
    srv_serror_rate DOUBLE PRECISION,
    same_srv_rate DOUBLE PRECISION,
    dst_host_srv_count INTEGER,
    dst_host_same_srv_rate DOUBLE PRECISION,
    dst_host_serror_rate DOUBLE PRECISION,
    dst_host_srv_serror_rate DOUBLE PRECISION,
    flag VARCHAR(10)
);

-- RLS (Row Level Security)
ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own decisions" ON decisions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own decisions" ON decisions
    FOR INSERT WITH CHECK (auth.uid() = user_id);
```

## 3. INTERFEJS UŻYTKOWNIKA (GRADIO)

### 3.1 Struktura aplikacji Gradio
```
Gradio App:
├── Login Tab (domyślny)
├── Register Tab
├── Main Analysis Tab (tylko dla zalogowanych)
└── Logout Button
```

### 3.2 Komponenty Gradio
- **Login Interface**: 
  - Email input
  - Password input
  - Login button
  - Register link
- **Register Interface**:
  - Email input
  - Password input
  - Confirm password input
  - Register button
  - Login link
- **Main Interface** (po zalogowaniu):
  - Traffic analysis form
  - Batch upload
  - Results display
  - Logout button

### 3.3 Walidacja w Gradio
- **Email**: Podstawowa walidacja formatu
- **Password**: Minimum 8 znaków (zgodnie z Supabase)
- **Confirm password**: Musi być identyczne
- **Błędy**: Wyświetlane w interfejsie Gradio

## 4. ENDPOINTS API (FASTAPI + SUPABASE)

### 4.1 Endpoints autentykacji
| Endpoint | Metoda | Wejście | Wyjście | Uwagi |
|----------|--------|---------|---------|-------|
| `/auth/register` | POST | `{email, password, confirm_password}` | `201` / `400` | Rejestracja przez Supabase |
| `/auth/login` | POST | `{email, password}` | `200 + token` / `401` | Logowanie przez Supabase |
| `/auth/logout` | POST | `(auth header)` | `200` | Wylogowanie |
| `/auth/forgot-password` | POST | `{email}` | `200` / `404` | Reset hasła (opcjonalnie) |

### 4.2 Modele Pydantic
```python
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    token: str
    user_id: str  # UUID from Supabase
    email: str
```

### 4.3 Middleware autentykacji
```python
async def verify_credentials(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> str:
    """Weryfikuje JWT token z Supabase i zwraca user_id"""
    try:
        supabase = get_supabase_client()
        user = await supabase.get_user(credentials.credentials)
        
        if not user or not user.get('user', {}).get('id'):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return user['user']['id']
        return user['user']['id']
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")
```

## 5. INTEGRACJA Z GRADIO

### 5.1 Flow autentykacji
1. **Start aplikacji**: Gradio wyświetla login tab
2. **Logowanie**: Użytkownik wprowadza dane → POST do FastAPI → Supabase Auth
3. **Sukces**: JWT token zapisywany w session state Gradio
4. **Dostęp**: Main tab staje się dostępny
5. **API calls**: Wszystkie wywołania API z tokenem w header

### 5.2 Session management w Gradio
```python
# Przykład implementacji
def login(email, password):
    response = requests.post("/auth/login", json={"email": email, "password": password})
    if response.status_code == 200:
        data = response.json()
        gr.State.update({
            "token": data["token"], 
            "user_id": data["user_id"],
            "email": data["email"]
        })
        return gr.Tabs.update(selected=1)  # Przejście do main tab
    else:
        return "Błąd logowania"

def logout():
    requests.post("/auth/logout", headers={"Authorization": f"Bearer {gr.State.get('token')}"})
    gr.State.update({"token": None, "user_id": None, "email": None})
    return gr.Tabs.update(selected=0)  # Powrót do login tab
```

## 6. KONFIGURACJA SUPABASE (LOKALNA)

### 6.1 Docker Compose
```yaml
services:
  supabase:
    image: supabase/supabase-dev
    ports:
      - "54321:54321"
    environment:
      POSTGRES_PASSWORD: postgres
      JWT_SECRET: your-super-secret-jwt-token
    volumes:
      - supabase_data:/var/lib/postgresql/data
```

### 6.2 Konfiguracja aplikacji
```python
# src/core/config/supabaseconfig.py
SUPABASE_URL = "http://127.0.0.1:54321"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Lokalny klucz
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Lokalny klucz
```

## 7. BEZPIECZEŃSTWO (MVP)

### 7.1 Ograniczenia bezpieczeństwa
- **Lokalne środowisko**: Brak HTTPS (nie wymagane lokalnie)
- **Proste hasła**: Minimum 8 znaków (zgodnie z Supabase)
- **Brak rate limiting**: Nie wymagane w MVP
- **Brak 2FA**: Nie wymagane w MVP

### 7.2 Implementowane zabezpieczenia
- **Supabase Auth**: Profesjonalny system autentykacji
- **JWT tokens**: Bezpieczne tokeny sesji
- **Row Level Security**: Ochrona danych użytkowników
- **Walidacja input**: Pydantic schemas
- **Session timeout**: Konfigurowalne przez Supabase

## 8. MIGRACJA DO PRODUKCJI

### 8.1 Przyszłe rozszerzenia (po MVP)
- **Cloud Supabase**: Migracja do Supabase Cloud
- **Email confirmation**: Włączenie potwierdzenia email
- **Password reset**: Funkcjonalność resetowania hasła
- **Role management**: Zaawansowane role użytkowników
- **Audit logs**: Logowanie działań użytkowników
- **OAuth providers**: Google, GitHub, etc.

### 8.2 Plan migracji
1. **MVP**: Lokalny Supabase + Gradio
2. **v1.1**: Migracja do Supabase Cloud
3. **v1.2**: Email confirmation i password reset
4. **v1.3**: Zaawansowane role i audit

## 9. TESTY I WALIDACJA

### 9.1 Testy jednostkowe
- Walidacja formularzy Gradio
- Integracja z Supabase Auth
- Generowanie i weryfikacja JWT
- Integracja Gradio-FastAPI-Supabase

### 9.2 Testy integracyjne
- Pełny flow rejestracji/logowania
- Dostęp do chronionych endpointów
- Session management w Gradio
- Logout i cleanup
- Row Level Security

## 10. DOKUMENTACJA

### 10.1 Dla użytkowników
- Instrukcja rejestracji i logowania
- Opis interfejsu Gradio
- Troubleshooting common issues

### 10.2 Dla developerów
- API documentation (Swagger)
- Supabase schema i RLS
- Authentication flow diagrams
- Local development setup
- Deployment guide

## 11. SETUP LOKALNY

### 11.1 Uruchomienie Supabase
```bash
# Uruchomienie lokalnego Supabase
supabase start

# Sprawdzenie statusu
supabase status
```

### 11.2 Konfiguracja aplikacji
```bash
# Ustawienie zmiennych środowiskowych
export SUPABASE_URL="http://127.0.0.1:54321"
export SUPABASE_ANON_KEY="your-local-anon-key"
export SUPABASE_SERVICE_ROLE_KEY="your-local-service-role-key"
```

---

**Uwaga**: Ta specyfikacja wykorzystuje Supabase jako system autentykacji, ale uruchamiany lokalnie, co zapewnia profesjonalne rozwiązanie autentykacji przy zachowaniu trybu offline-first wymaganego przez PRD.

