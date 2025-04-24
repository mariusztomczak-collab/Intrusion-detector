# Dokument wymagań produktu (PRD) - Detektor Ruchu Złośliwego

## 1. Przegląd produktu
Celem projektu jest stworzenie aplikacji webowej, działającej również lokalnie (w kontenerze Docker), która umożliwia klasyfikację ruchu sieciowego jako złośliwego lub normalnego. Klasyfikacja będzie dokonywana przez wytrenowany model uczenia maszynowego (ML), bazujący na zbiorze danych KD-NSL. Aplikacja będzie wykorzystywana przez funkcjonariuszy organów ścigania w celu automatycznej analizy zdarzeń sieciowych. Interfejs użytkownika będzie oparty na frameworku Gradio i zapewni prostotę obsługi dla osób nietechnicznych.

## 2. Problem użytkownika
Obecnie funkcjonariusze analizują dane o ruchu sieciowym ręcznie, co jest czasochłonne i podatne na błędy. Brakuje prostego narzędzia, które umożliwiłoby szybką i zautomatyzowaną klasyfikację zdarzeń jako złośliwych lub normalnych. Użytkownicy potrzebują intuicyjnego rozwiązania, które pozwoli na szybką reakcję bez konieczności głębokiej analizy technicznej.

## 3. Wymagania funkcjonalne
- Klasyfikacja danych sieciowych na podstawie modelu ML (złośliwy/normalny).
- Obsługa dwóch trybów danych wejściowych:
  - Pojedyncze zapytania w formacie JSON przez UI.
  - Wsadowe zapytania przez endpoint FastAPI.
- Walidacja danych wejściowych (struktura i wartości) przy użyciu Pydantic.
- Historia zapytań i odpowiedzi zapisywana lokalnie, bez przeszukiwania.
- Lokalny zapis logów systemowych.
- Automatyczna dokumentacja API (Swagger UI).
- Obsługa jako webserwis offline-first, uruchamiany z Dockera.
- Model ML działa jako niezależny mikroserwis.
- Minimalistyczny UI na Gradio.

## 4. Granice produktu
- Brak przeszukiwania historii zapytań przez użytkownika.
- Brak ręcznej ingerencji w etykiety klasyfikacyjne (brak feedback loop).
- Brak eksportu wyników klasyfikacji.
- Brak integracji z zewnętrznymi systemami SIEM.
- Brak zabezpieczeń endpointów na etapie MVP.
- Brak trybu testowego z przykładowymi danymi.
- Brak zaawansowanego dashboardu technicznego.
- Model ML nie podlega retrainingowi w wersji MVP.
- Brak polityki retencji danych i wersjonowania komponentów (tymczasowo).

## 5. Historyjki użytkowników

### US-001 - Klasyfikacja pojedynczego zdarzenia
- Opis: Jako funkcjonariusz, chcę móc wprowadzić dane ruchu sieciowego w formacie JSON, aby dowiedzieć się, czy są one złośliwe.
- Kryteria akceptacji:
  - Użytkownik może wprowadzić dane przez interfejs Gradio.
  - Aplikacja zwraca klasyfikację: "złośliwy" lub "normalny".
  - Błędnie sformatowane dane są odrzucane z komunikatem o błędzie.

### US-002 - Przesłanie danych wsadowych
- Opis: Jako funkcjonariusz, chcę przesłać plik z wieloma zdarzeniami przez API, aby uzyskać klasyfikację dla każdej pozycji.
- Kryteria akceptacji:
  - Endpoint FastAPI przyjmuje wsadowe dane (np. JSONL/CSV).
  - Aplikacja przetwarza poprawne rekordy i generuje raport błędów dla niepoprawnych.
  - Dokumentacja API jest dostępna w formacie Swagger UI.

### US-003 - Zobaczenie wyników klasyfikacji
- Opis: Jako funkcjonariusz, chcę zobaczyć wynik klasyfikacji od razu po przesłaniu danych, abym mógł podjąć decyzję.
- Kryteria akceptacji:
  - Wynik klasyfikacji jest wyświetlany natychmiast po przetworzeniu danych.
  - Aplikacja nie wymaga ponownego załadunku ani dodatkowych kroków.

### US-004 - Obsługa błędnych danych
- Opis: Jako funkcjonariusz, chcę być poinformowany, jeśli w przesłanych danych występują błędy, abym mógł je poprawić.
- Kryteria akceptacji:
  - Aplikacja wskazuje, które rekordy zawierają błędy.
  - Komunikat zawiera informację o rodzaju błędu (np. brak pola, nieprawidłowy typ).

### US-005 - Uruchomienie aplikacji lokalnie
- Opis: Jako technik IT, chcę móc uruchomić aplikację z obrazu Dockera, aby działała bez dostępu do internetu.
- Kryteria akceptacji:
  - Udostępniony jest plik Dockerfile i opcjonalnie docker-compose.yml.
  - Aplikacja działa offline i nie wymaga zewnętrznych zależności.

### US-006 - Monitorowanie działania modelu (techniczne)
- Opis: Jako administrator, chcę móc śledzić metryki jakości modelu, aby upewnić się, że działa prawidłowo.
- Kryteria akceptacji:
  - MLflow loguje jakość modelu.
  - Dane MLflow są niedostępne dla użytkowników końcowych.
  - Logi aplikacji zapisywane są w lokalnych plikach.

## 6. Metryki sukcesu
- Dokładność klasyfikacji powyżej 90% na danych testowych.
- Precyzja i recall powyżej 85%.
- Średni czas odpowiedzi na pojedyncze zapytanie poniżej 2 sekund.
- 100% pokrycia walidacji błędnych danych (wszystkie niepoprawne przypadki są wykrywane).
- Pomyślne wdrożenie lokalne na min. 3 typowych środowiskach użytkownika (Windows, Linux, macOS).
- Brak błędów krytycznych podczas testów integracyjnych Dockera.


