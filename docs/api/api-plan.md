# REST API Plan

## 1. Zasoby

| Resource       | Tabela bazy danych     | Opis                                                |
|----------------|------------------------|-----------------------------------------------------|
| `users`        | `users`                | Administratorzy korzystający z systemu.            |
| `decisions`    | `decisions`            | Historia klasyfikacji (pojedyncze i wsadowe).      |

---

## 2. Punkty końcowe

### `/users`

#### GET `/users`
- **Opis**: Pobierz listę aktywnych użytkowników (adminów).
- **Parametry zapytania**:
  - `active` (opcjonalne): `true/false` – filtruj po aktywności
- **Odpowiedź**:
```json
[
  {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "created_at": "2024-01-01T12:00:00",
    "is_active": true
  }
]
```
- **Kody sukcesu**: `200 OK`
- **Kody błędów**: `401 Unauthorized`, `500 Internal Server Error`

---

### `/decisions`

#### POST `/decisions/single`
- **Opis**: Klasyfikacja pojedynczego zdarzenia sieciowego.
- **Request JSON**:
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
  "correlation_id": "uuid-string",
  "model_version": "v1.0.0"
}
```
- **Odpowiedź**:
```json
{
  "classification_result": "MALICIOUS",
  "timestamp": "2025-06-06T13:05:00",
  "correlation_id": "uuid-string"
}
```
- **Kody sukcesu**: `201 Created`
- **Kody błędów**: `400 Bad Request`, `401 Unauthorized`, `500 Internal Server Error`

---

#### POST `/decisions/batch`
- **Opis**: Przesyłanie i klasyfikacja wsadowych danych (np. plik CSV lub JSONL).
- **Request**: multipart/form-data z plikiem wsadowym.
- **Odpowiedź**:
```json
{
  "summary": {
    "processed": 20,
    "errors": 2,
    "successful": 18
  },
  "report": [
    {
      "correlation_id": "uuid1",
      "classification_result": "NORMAL"
    },
    {
      "correlation_id": "uuid2",
      "error": "Missing field 'flag'"
    }
  ]
}
```
- **Kody sukcesu**: `202 Accepted`
- **Kody błędów**: `400 Bad Request`, `422 Unprocessable Entity`, `500 Internal Server Error`

---

#### GET `/decisions`
- **Opis**: Lista wszystkich klasyfikacji (dla admina lub dla user_id).
- **Parametry zapytania**:
  - `user_id` (opcjonalnie)
  - `source_type` (opcjonalnie): `single`, `batch`
  - `classification_result` (opcjonalnie): `NORMAL`, `MALICIOUS`
  - `limit`, `offset` – paginacja
  - `sort` – np. `timestamp desc`
- **Odpowiedź**:
```json
[
  {
    "id": 1,
    "user_id": 1,
    "timestamp": "2025-06-06T12:00:00",
    "classification_result": "NORMAL",
    "source_type": "single"
  }
]
```
- **Kody sukcesu**: `200 OK`
- **Kody błędów**: `401 Unauthorized`, `500 Internal Server Error`

---

## 3. Uwierzytelnianie i autoryzacja

- **Mechanizm**: HTTP Basic Auth (MVP) z planowaną rozbudową do JWT lub OAuth2.
- **Dane logowania**: weryfikowane lokalnie przez porównanie `password_hash` (bcrypt/argon2).
- **Dostęp do punktów końcowych**:
  - `/users`: tylko `admin`
  - `/decisions/*`: autoryzowany użytkownik
- **Brak rejestracji użytkowników przez API (tylko przez panel CLI/admin)**

---

## 4. Walidacja i logika biznesowa

### 🔒 Walidacja danych wejściowych (Pydantic):
- Wszystkie pola cech (`features`) wymagane w `single`
- `flag` – tylko wartości akceptowalne zgodne z KD-NSL
- `source_type` – tylko `single` lub `batch`
- `classification_result` – tylko `NORMAL` lub `MALICIOUS`

### 🧠 Logika biznesowa

| Funkcja                                | Implementacja                                          |
|----------------------------------------|--------------------------------------------------------|
| Klasyfikacja zdarzenia (`US-001`)      | `/decisions/single`                                   |
| Klasyfikacja wsadowa (`US-002`)        | `/decisions/batch`                                    |
| Informacja o błędach (`US-004`)        | Raport błędów w `/decisions/batch`                    |
| Historia klasyfikacji (`US-003`)       | `/decisions`, filtr `user_id` lub `correlation_id`    |
| Brak feedback loop / edycji danych     | Brak metod PUT/PATCH/DELETE                           |
| Logika uruchomienia offline            | Realizowane przez Docker, poza zakresem API REST      |

### 📈 Wydajność:
- Indeksy w bazie na: `timestamp`, `user_id`, `correlation_id`, `classification_result`, `source_type`
- Paginacja i sortowanie dostępne w GET `/decisions`

---


