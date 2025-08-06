sup# PostgreSQL Schema for Intrusion Detection MVP (Extended with `users` table)

## 1. Tables

### Table: users

This table is managed by Supabase Auth

| Column name     | Data type  | Constraints                        | Description                             |
|------------------|------------|------------------------------------|-----------------------------------------|
| id               | SERIAL     | PRIMARY KEY                        | Unikalny identyfikator użytkownika      |
| username         | TEXT       | UNIQUE NOT NULL                    | Nazwa użytkownika                       |
| password_hash    | TEXT       | NOT NULL                           | Hasz hasła                              |
| role
---
             | TEXT       | NOT NULL CHECK (role IN ('admin')) | Rola użytkownika (na razie tylko `admin`) |
| created_at       | TIMESTAMP  | NOT NULL DEFAULT CURRENT_TIMESTAMP | Data utworzenia konta                   |
| is_active        | BOOLEAN    | NOT NULL DEFAULT TRUE              | Status aktywności użytkownika           |

---

### Table: decisions

| Column name             | Data type      | Constraints                                        | Description                                                      |
|-------------------------|----------------|----------------------------------------------------|------------------------------------------------------------------|
| id                      | SERIAL         | PRIMARY KEY                                        | Unikalny identyfikator rekordu                                   |
| user_id                 | INTEGER        | NOT NULL REFERENCES users(id)                      | Klucz obcy do użytkownika wykonującego klasyfikację              |
| timestamp               | TIMESTAMP      | NOT NULL DEFAULT CURRENT_TIMESTAMP                 | Czas utworzenia rekordu                                          |
| correlation_id          | TEXT           | NOT NULL                                           | Unikalny identyfikator zapytania wygenerowany przez aplikację    |
| source_type             | TEXT           | NOT NULL CHECK (source_type IN ('single', 'batch'))| Typ zapytania (pojedyncze lub wsadowe)                           |
| batch_filename          | TEXT           | NULL                                               | Nazwa pliku wsadowego (jeśli dotyczy)                           |
| batch_file_contents     | TEXT           | NULL                                               | Surowa zawartość pliku wsadowego (opcjonalnie)                  |
| model_version           | TEXT           | NULL                                               | Wersja modelu ML                                                 |
| classification_result   | TEXT           | NOT NULL CHECK (classification_result IN ('NORMAL', 'MALICIOUS')) | Wynik klasyfikacji                                               |

#### Cecha wejściowa – dane z modelu KD-NSL (utrzymywane jako kolumny jawne dla optymalizacji)

| Feature                          | Data type      | Constraints  |
|----------------------------------|----------------|--------------|
| logged_in                        | BOOLEAN        | NOT NULL     |
| count                            | INTEGER        | NOT NULL     |
| serror_rate                      | DOUBLE PRECISION | NOT NULL   |
| srv_serror_rate                 | DOUBLE PRECISION | NOT NULL   |
| same_srv_rate                   | DOUBLE PRECISION | NOT NULL   |
| dst_host_srv_count              | INTEGER        | NOT NULL     |
| dst_host_same_srv_rate         | DOUBLE PRECISION | NOT NULL   |
| dst_host_serror_rate           | DOUBLE PRECISION | NOT NULL   |
| dst_host_srv_serror_rate       | DOUBLE PRECISION | NOT NULL   |
| flag                             | VARCHAR(10)    | NOT NULL     |

---

## 2. Relationships

- `decisions.user_id` → `users.id` (wiele decyzji może pochodzić od jednego użytkownika).
- Zależność jeden-do-wielu: jeden użytkownik → wiele klasyfikacji.

---

## 3. Indexes

```sql
CREATE INDEX idx_users_username ON users (username);
CREATE INDEX idx_decisions_timestamp ON decisions (timestamp);
CREATE INDEX idx_decisions_correlation_id ON decisions (correlation_id);
CREATE INDEX idx_decisions_classification_result ON decisions (classification_result);
CREATE INDEX idx_decisions_model_version ON decisions (model_version);
CREATE INDEX idx_decisions_source_type ON decisions (source_type);
CREATE INDEX idx_decisions_flag ON decisions (flag);
CREATE INDEX idx_decisions_user_id ON decisions (user_id);

