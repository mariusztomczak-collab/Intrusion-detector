# Zaktualizowany stos technologiczny (MVP) - Detektor Ruchu Złośliwego

## Frontend
- **Gradio**  
  Lekki i szybki framework do tworzenia prostych interfejsów użytkownika w Pythonie. Idealny do prezentacji klasyfikacji w formie formularza z natychmiastową odpowiedzią.

## Backend
- **FastAPI**  
  Wydajny i nowoczesny framework do tworzenia REST API w Pythonie. Obsługuje walidację danych, automatyczne dokumentowanie endpointów (Swagger UI) i łatwą integrację z innymi komponentami.

- **Uwierzytelnianie (Auth)**  
  - **HTTP Basic Auth** lub **JWT (JSON Web Tokens)** – do ochrony endpointów API.
  - Prosty system zarządzania użytkownikami z lokalną bazą danych (PostgreSQL).
  - Możliwość rozszerzenia w przyszłości do OAuth2/LDAP, jeśli zajdzie taka potrzeba.

## Model ML
- **Wytrenowany model ML (Python pickle / joblib / ONNX)**  
  - Wczytywany jako mikroserwis lub lokalna funkcja w backendzie.
  - Klasyfikuje dane jako „złośliwe” lub „normalne” na podstawie przetworzonych cech z KD-NSL.

## Monitoring i obserwowalność
- **MLflow**  
  Narzędzie do śledzenia metryk modelu, wersjonowania i zarządzania eksperymentami ML.
  - Niedostępne dla użytkowników końcowych.
  - Wykorzystywane przez zespół projektowy do oceny jakości i poprawności modelu.

## Baza danych
- **PostgreSQL**  
  Relacyjna baza danych do przechowywania historii zapytań, odpowiedzi, użytkowników oraz metadanych systemowych.

## Cache (opcjonalnie w późniejszej fazie)
- **Brak Redis w MVP**  
  Można dodać po walidacji produktu, gdy pojawi się potrzeba optymalizacji szybkości zapytań.

## Konteneryzacja i uruchamianie
- **Docker + Docker Compose**  
  - Każdy komponent (frontend, backend, baza danych, MLflow) jako osobny serwis w `docker-compose.yml`.
  - Umożliwia szybki start środowiska lokalnego i testowego.
  - Zapewnia izolację i spójność uruchamiania niezależnie od systemu operacyjnego użytkownika.

## CI/CD i hosting
- **GitHub Actions**  
  - Automatyczne budowanie i testowanie obrazów Dockera.
  - Możliwość wdrożenia staging/production z webhookiem.

- **DigitalOcean (Docker Droplet / App Platform)**  
  - Hostowanie aplikacji bez potrzeby użycia Kubernetes.
  - Obsługa pojedynczych instancji aplikacji webowych opartych na Dockerze.
  - Możliwość rozszerzenia o load balancer, backup i monitoring.

---

## Diagram architektury (MVP)


