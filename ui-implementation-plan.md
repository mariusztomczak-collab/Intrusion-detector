# Plan implementacji widoku klasyfikacji pojedynczego zdarzenia

## 1. Przegląd
Widok umożliwia użytkownikowi końcowemu przesłanie pojedynczego zestawu danych ruchu sieciowego w formacie JSON w celu sklasyfikowania go jako „NORMAL” lub „MALICIOUS”. Wynik jest wyświetlany natychmiast w interfejsie użytkownika. Widok obejmuje formularz wejściowy, komponent wyświetlania wyniku, obsługę błędów i integrację z Supabase + FastAPI.

## 2. Routing widoku
Ścieżka: `/classify/single` (wewnętrzna zakładka interfejsu Gradio)

## 3. Struktura komponentów
- `ClassificationSingleTab` (główny komponent widoku)
  - `FeatureInputForm` – formularz JSON z danymi wejściowymi
  - `SubmitButton` – przycisk do wysyłki
  - `ResultBox` – pole z wynikiem klasyfikacji
  - `ErrorMessage` – komunikat o błędzie (jeśli wystąpi)

## 4. Szczegóły komponentów

### ClassificationSingleTab
- **Opis**: Główna sekcja widoku klasyfikacji pojedynczego zdarzenia.
- **Elementy**: `FeatureInputForm`, `SubmitButton`, `ResultBox`, `ErrorMessage`
- **Interakcje**: Przesyłanie formularza, wyświetlenie wyniku, obsługa błędów
- **Walidacja**: Sprawdzenie kompletności danych wejściowych i ich typów przed wysyłką
- **Typy**:
  - `SingleClassificationInput`
  - `SingleClassificationResult`
- **Propsy**: `user_id`, `token`, `model_version`

### FeatureInputForm
- **Opis**: Pole edycji danych wejściowych (JSON)
- **Elementy**: `gr.JSON` lub `gr.Textbox`, z predefiniowanym szablonem
- **Interakcje**: Edycja przez użytkownika
- **Walidacja**: Format JSON, obecność wymaganych pól
- **Typy**: `SingleClassificationInput.features`

### SubmitButton
- **Opis**: Przycisk wysyłający dane do backendu
- **Elementy**: `gr.Button`
- **Interakcje**: `on_click` → wywołanie API
- **Walidacja**: Wywołanie tylko jeśli dane są kompletne i poprawne

### ResultBox
- **Opis**: Wyświetlenie wyniku klasyfikacji z backendu
- **Elementy**: `gr.Textbox`, `gr.Label`, stylizacja koloru
- **Interakcje**: Odbiór danych z API

### ErrorMessage
- **Opis**: Komunikaty walidacyjne lub błędów serwera
- **Elementy**: `gr.Label` (ukryty do czasu błędu)
- **Interakcje**: Wyświetlenie po błędnej walidacji lub błędzie z API

## 5. Typy

### SingleClassificationInput
```python
{
  features: {
    logged_in: bool,
    count: int,
    serror_rate: float,
    srv_serror_rate: float,
    same_srv_rate: float,
    dst_host_srv_count: int,
    dst_host_same_srv_rate: float,
    dst_host_serror_rate: float,
    dst_host_srv_serror_rate: float,
    flag: str
  },
  user_id: int,
  correlation_id: str,
  model_version: str
}

