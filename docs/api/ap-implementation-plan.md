# API Endpoint Implementation Plan: POST `/decisions/single`

## 1. Przegląd punktu końcowego
Ten punkt końcowy umożliwia przesłanie pojedynczego zdarzenia sieciowego w celu klasyfikacji przez wytrenowany model ML, który jest zarejestrowany i zarządzany przez serwer MLflow. Wynik klasyfikacji ("MALICIOUS" lub "NORMAL") wraz z metadanymi jest zapisywany w tabeli `decisions`. Endpoint działa w trybie synchronicznym — odpowiedź zwracana jest natychmiast po przetworzeniu.

## 2. Szczegóły żądania
- **Metoda HTTP**: POST  
- **Struktura URL**: `/decisions/single`  
- **Parametry**:
  - **Wymagane**:
    - `features.logged_in`: `bool`
    - `features.count`: `int`
    - `features.serror_rate`: `float`
    - `features.srv_serror_rate`: `float`
    - `features.same_srv_rate`: `float`
    - `features.dst_host_srv_count`: `int`
    - `features.dst_host_same_srv_rate`: `float`
    - `features.dst_host_serror_rate`: `float`
    - `features.dst_host_srv_serror_rate`: `float`
    - `features.flag`: `str` (np. `"S0"`)
    

- **Request Body**:
```json
{
  "features": {
    "logged_in": true,
    "count": 45,
    "serror_rate": 0.05,
    "srv_serror_rate": 0.04,
    "same_srv_rate": 0.88,
    "dst_host_srv_count": 110,
    "dst_host_same_srv_rate": 0.99,
    "dst_host_serror_rate": 0.02,
    "dst_host_srv_serror_rate": 0.01,
    "flag": "S0"
  },
  "user_id": 1,
  "correlation_id": "abc123-def456",
  "model_version": "v1.0.0"
}
```

## 3. Szczegóły odpowiedzi

```json
{
  "classification_result": "MALICIOUS",
  "timestamp": "2025-06-06T13:05:00",
  "correlation_id": "abc123-def456"
}
```

- **Statusy**:
  - `201 Created` – klasyfikacja zakończona powodzeniem
  - `400 Bad Request` – brak lub nieprawidłowe dane wejściowe
  - `401 Unauthorized` – brak autoryzacji
  - `404 Not Found` – model ML lub użytkownik nie znaleziony
  - `500 Internal Server Error` – błąd klasyfikatora ML lub bazy

## 4. Przepływ danych

1. FastAPI przyjmuje żądanie z danymi cech.
2. Uwierzytelnienie następuje przez HTTP Basic Auth.
3. Dane są walidowane (Pydantic) i przekazywane do `DecisionService`.
4. `DecisionService` lokalizuje model ML:
   - Za pomocą klienta MLflow (`mlflow.pyfunc.load_model(model_uri)`) ładuje model zarejestrowany jako `models:/intrusion-detector/<model_version>`.
5. Model jest wywoływany lokalnie w procesie lub jako serwis HTTP (zależnie od konfiguracji).
6. Otrzymana klasyfikacja jest zapisywana w bazie danych (`decisions`).
7. Zwracana jest odpowiedź JSON.

## 5. Względy bezpieczeństwa

- Uwierzytelnienie: HTTP Basic Auth
- Autoryzacja: użytkownik `user_id` musi istnieć i być aktywny
- Walidacja danych cech i ID użytkownika
- Ograniczony dostęp do modelu MLflow: jedynie backend ma dostęp do lokalnego lub zdalnego serwera MLflow

## 6. Obsługa błędów

| Błąd | Kod | Obsługa |
|------|-----|--------|
| Brak autoryzacji | 401 | Middleware FastAPI |
| Brak wymaganych pól | 400 | Walidacja Pydantic |
| Błędne dane cech (np. `flag`) | 400 | Zwracany opisowy komunikat |
| Nieistniejący użytkownik | 404 | Sprawdzenie w bazie danych |
| Model ML nieznaleziony (MLflow) | 404 | Obsługa wyjątku `mlflow.exceptions` |
| Błąd modelu ML | 500 | Log + ogólny komunikat |
| Błąd INSERT do bazy | 500 | Log + rollback transakcji |

## 7. Rozważania dotyczące wydajności

- Model ML wczytywany na podstawie wersji — możliwe cache’owanie (`lru_cache`) instancji modelu.
- Model lokalny (pickle/joblib) jest szybki — czasy odpowiedzi <2s.
- Wersja modelu może być parametrem dla routingów MLflow — wspiera wersjonowanie.
- Można dodać rate limiting na poziomie endpointu FastAPI.

## 8. Etapy wdrożenia

1. Zdefiniuj schemat wejściowy Pydantic `DecisionInputSchema`
2. Zaimplementuj klasę `DecisionService` z metodami:
   - `load_model(model_version)`
   - `predict(features)`
   - `save_decision(user_id, result, correlation_id, ...)`
3. Skonfiguruj klienta MLflow (lokalny lub zdalny tracking URI)
4. Utwórz endpoint POST `/decisions/single` w FastAPI
5. Wprowadź mechanizm walidacji `user_id` z bazy danych
6. Obsłuż wyjątki modelu MLflow oraz błędy predykcji
7. Zaloguj błędy i metadane (do logów aplikacji)
8. Przetestuj wszystkie ścieżki: poprawne, błędne, brak modelu, złe dane
9. Zaktualizuj dokumentację Swagger (`@app.post(...)` + opis)
10. Pokryj testami jednostkowymi i integracyjnymi (Mock MLflow)


