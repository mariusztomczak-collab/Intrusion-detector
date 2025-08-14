# 🎯 User Guide - Intrusion Detector

**Przewodnik dla użytkowników zewnętrznych - jak uruchomić aplikację lokalnie**

## 🚀 Szybki start (5 minut)

### **Krok 1: Sklonuj repozytorium**
```bash
git clone https://github.com/twoje-repo/intrusion-detector.git
cd intrusion-detector
```

### **Krok 2: Skonfiguruj środowisko**
```bash
# Skopiuj przykładowy plik konfiguracyjny
cp .env.example .env

# Lub utwórz ręcznie:
echo "MLFLOW_TRACKING_URI=local" > .env
```

### **Krok 3: Uruchom aplikację**
```bash
# Uruchom aplikację
./start.sh

# Lub w trybie lokalnym (zalecane):
./start.sh --local
```

### **Krok 4: Otwórz aplikację**
- 🌐 **Interfejs webowy**: http://localhost:7860
- 🔧 **API**: http://localhost:8000
- 📊 **Dokumentacja API**: http://localhost:8000/docs

---

## 📋 Wymagania systemowe

### **Minimalne wymagania:**
- **Python 3.12+**
- **4GB RAM**
- **1GB wolnego miejsca na dysku**
- **Porty 8000 i 7860 dostępne**

### **Opcjonalne:**
- **Docker** (dla trybu kontenerowego)
- **Git** (do klonowania repozytorium)

---

## 🔧 Szczegółowa instrukcja

### **1. Przygotowanie środowiska**

**Sprawdź czy masz Python:**
```bash
python3 --version
# Powinno pokazać Python 3.12 lub nowszy
```

**Sprawdź czy masz Git:**
```bash
git --version
# Powinno pokazać wersję Git
```

### **2. Sklonowanie repozytorium**

```bash
# Sklonuj repozytorium
git clone https://github.com/twoje-repo/intrusion-detector.git

# Przejdź do katalogu projektu
cd intrusion-detector

# Sprawdź czy masz wszystkie pliki
ls -la
```

Powinieneś zobaczyć:
- `start.sh` - skrypt uruchomieniowy
- `stop.sh` - skrypt zatrzymujący
- `status.sh` - skrypt sprawdzający status
- `artifacts/` - katalog z modelami ML
- `src/` - kod źródłowy aplikacji

### **3. Konfiguracja**

**Utwórz plik `.env`:**
```bash
# Utwórz plik konfiguracyjny
cat > .env << EOF
# Konfiguracja dla trybu end-user (bez MLflow)
MLFLOW_TRACKING_URI=local

# Konfiguracja Supabase (domyślne wartości)
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU
EOF
```

### **4. Uruchomienie aplikacji**

**Opcja A: Tryb lokalny (zalecane)**
```bash
# Uruchom w trybie lokalnym
./start.sh --local

# Lub po prostu:
./start.sh
```

**Opcja B: Tryb Docker (dla zaawansowanych)**
```bash
# Uruchom w trybie Docker
./start.sh --docker
```

### **5. Sprawdzenie statusu**

```bash
# Sprawdź czy wszystko działa
./status.sh
```

Powinieneś zobaczyć:
```
✅ Environment configured
✅ Model files found
✅ Services running
✅ FastAPI: http://localhost:8000
✅ Gradio UI: http://localhost:7860
```

### **6. Dostęp do aplikacji**

Po uruchomieniu aplikacja będzie dostępna pod adresami:

| Usługa | URL | Opis |
|--------|-----|------|
| 🌐 **Interfejs webowy** | http://localhost:7860 | Główny interfejs użytkownika |
| 🔧 **API** | http://localhost:8000 | Endpoint API |
| 📊 **Dokumentacja API** | http://localhost:8000/docs | Swagger UI |
| ❤️ **Health check** | http://localhost:8000/health | Status aplikacji |

---

## 🎯 Pierwsze użycie

### **1. Rejestracja użytkownika**

1. Otwórz przeglądarkę i przejdź do http://localhost:7860
2. Kliknij "Register" lub "Zarejestruj się"
3. Wprowadź swój email i hasło
4. Potwierdź rejestrację

### **2. Logowanie**

1. Wprowadź swój email i hasło
2. Kliknij "Login" lub "Zaloguj się"

### **3. Analiza ruchu sieciowego**

1. Po zalogowaniu zobaczysz interfejs analizy
2. Wprowadź dane ruchu sieciowego
3. Kliknij "Analyze" lub "Analizuj"
4. Zobacz wynik: **Normal** lub **Malicious**

---

## 🛠️ Zarządzanie aplikacją

### **Sprawdzanie statusu**
```bash
./status.sh
```

### **Zatrzymanie aplikacji**
```bash
./stop.sh
```

### **Restart aplikacji**
```bash
./stop.sh && ./start.sh
```

### **Podgląd logów**
```bash
# Wszystkie logi
tail -f logs/*.log

# Tylko logi FastAPI
tail -f logs/fastapi.log

# Tylko logi Gradio
tail -f logs/gradio.log
```

---

## 🔧 Rozwiązywanie problemów

### **Problem: "Permission denied" przy uruchamianiu skryptów**
```bash
# Nadaj uprawnienia wykonywania
chmod +x start.sh stop.sh status.sh
```

### **Problem: "Port already in use"**
```bash
# Sprawdź co używa portów
lsof -i :8000
lsof -i :7860

# Zatrzymaj aplikację
./stop.sh

# Sprawdź czy procesy zostały zatrzymane
./status.sh
```

### **Problem: "Model not found"**
```bash
# Sprawdź czy masz pliki modeli
ls -la artifacts/

# Powinieneś zobaczyć:
# - model.joblib
# - preprocessor.joblib
# - model_metadata.json
```

### **Problem: "Python not found"**
```bash
# Sprawdź czy Python jest zainstalowany
python3 --version

# Jeśli nie, zainstaluj Python 3.12+
# Ubuntu/Debian:
sudo apt update && sudo apt install python3.12

# macOS:
brew install python@3.12
```

### **Problem: "Module not found"**
```bash
# Zatrzymaj aplikację
./stop.sh

# Usuń wirtualne środowisko (jeśli istnieje)
rm -rf venv/

# Uruchom ponownie (skrypt utworzy nowe środowisko)
./start.sh --local
```

---

## 📞 Wsparcie

### **Gdzie szukać pomocy:**

1. **Dokumentacja projektu**: `docs/README.md`
2. **GitHub Issues**: https://github.com/twoje-repo/intrusion-detector/issues
3. **Logi aplikacji**: `logs/` katalog

### **Co sprawdzić przed zgłoszeniem problemu:**

- ✅ Czy masz Python 3.12+?
- ✅ Czy sklonowałeś całe repozytorium?
- ✅ Czy utworzyłeś plik `.env`?
- ✅ Czy porty 8000 i 7860 są wolne?
- ✅ Czy masz wystarczająco RAM (4GB+)?

### **Informacje do zgłoszenia problemu:**

```bash
# System info
uname -a
python3 --version
./status.sh

# Logi błędów
tail -20 logs/fastapi.log
tail -20 logs/gradio.log
```

---

## 🎉 Gratulacje!

Jeśli dotarłeś do tego miejsca, aplikacja powinna działać poprawnie! 

**Co możesz teraz robić:**
- 🔍 Analizować ruch sieciowy pod kątem intruzji
- 📊 Przeglądać historię analiz
- 🔧 Używać API do integracji z innymi systemami
- 📈 Monitorować wydajność modeli ML

**Następne kroki:**
- Przeczytaj dokumentację API: http://localhost:8000/docs
- Sprawdź przewodnik dewelopera: `docs/development/`
- Zgłoś problemy lub sugestie na GitHub

---

**🚀 Happy analyzing!** 🛡️
