# 🚀 CI/CD Pipeline Guide

**Automatyczny transfer kodu i testowanie CI/CD dla Intrusion Detector**

## 📋 Przegląd

Ten projekt zawiera kompleksowy CI/CD pipeline, który automatycznie:
1. **Testuje kod** - sprawdza jakość, bezpieczeństwo i funkcjonalność
2. **Buduje obrazy Docker** - weryfikuje konteneryzację
3. **Transferuje kod** - automatycznie aktualizuje repozytorium docelowe
4. **Dostarcza aplikację** - gotowa do użycia przez użytkowników zewnętrznych

## 🔄 Workflow GitHub Actions

### **Pliki workflow:**

| Plik | Opis | Trigger |
|------|------|---------|
| `pull-request.yml` | Testy dla Pull Requestów | `pull_request` |
| `transfer-and-deploy.yml` | **Transfer i deployment** | `push` + `workflow_dispatch` |

### **Struktura pipeline:**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Code Push     │───▶│  GitHub Actions │───▶│ Target Repo     │
│   (main)        │    │  CI/CD Pipeline │    │ (Transfer)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Test Results  │
                       │   & Reports     │
                       └─────────────────┘
```

## 🎯 Jobs w Pipeline

### **Job 1: Code Quality & Linting**
- **Black** - formatowanie kodu
- **isort** - sortowanie importów
- **flake8** - jakość kodu
- **mypy** - sprawdzanie typów

### **Job 2: Unit Tests & Coverage**
- Testy jednostkowe wszystkich modułów
- Pomiar pokrycia kodu
- Upload do Codecov

### **Job 3: Integration Tests**
- Testy integracyjne
- Testy API endpoints
- Testy bazy danych

### **Job 4: Security Analysis**
- **Bandit** - analiza bezpieczeństwa kodu
- **Safety** - sprawdzanie zależności

### **Job 5: Docker Build Test**
- Budowanie obrazów Docker
- Testowanie kontenerów
- Weryfikacja deploymentu

### **Job 6: Application Test**
- Test uruchomienia aplikacji
- Test ładowania modeli ML
- Weryfikacja funkcjonalności

### **Job 7: Transfer to Target Repository**
- **Automatyczny transfer** kodu do repozytorium docelowego
- Konfigurowalny target repository
- Opcja force push

### **Job 8: Notification**
- Powiadomienia o sukcesie/błędzie
- Podsumowanie wyników

## 🛠️ Jak używać

### **Automatyczny transfer (push do main):**
```bash
# Wszystkie zmiany w main branch automatycznie triggerują pipeline
git push origin main
```

### **Ręczny transfer (workflow_dispatch):**
1. Przejdź do **Actions** na GitHub
2. Wybierz **"Transfer and Deploy CI/CD"**
3. Kliknij **"Run workflow"**
4. Skonfiguruj parametry:
   - **Target repository**: `username/repo-name`
   - **Force push**: `true/false`

### **Lokalne testowanie:**
```bash
# Testuj pipeline lokalnie przed push
./scripts/test-ci-cd.sh

# Z opcjami
./scripts/test-ci-cd.sh --verbose
./scripts/test-ci-cd.sh --clean
```

## ⚙️ Konfiguracja

### **Zmienne środowiskowe:**
```yaml
env:
  PYTHON_VERSION: "3.12"
  PIP_CACHE_DIR: ~/.cache/pip
```

### **Dependencies między jobami:**
```yaml
needs: [lint, unit-tests, integration-tests, security-scan, docker-build, app-test]
```

### **Warunki uruchomienia:**
```yaml
if: success()  # Tylko jeśli poprzednie joby się powiodły
```

## 🔧 Customization

### **Zmiana target repository:**
```yaml
# W workflow_dispatch
target_repo:
  description: 'Target repository (username/repo)'
  default: 'mariusztomczak-collab/Intrusion-detector'
```

### **Dodanie nowych testów:**
```yaml
# Dodaj nowy job
new-test:
  name: New Test
  runs-on: ubuntu-latest
  needs: [lint]
  steps:
    - name: Run new test
      run: echo "New test"
```

### **Zmiana timeout:**
```yaml
timeout-minutes: 15  # Domyślnie 10 minut
```

## 📊 Monitoring i Raporty

### **GitHub Actions Dashboard:**
- **Actions** → **Transfer and Deploy CI/CD**
- Szczegółowe logi każdego joba
- Czas wykonania
- Status sukces/błąd

### **Artefakty:**
- **Security reports** - Bandit i Safety
- **Coverage reports** - Codecov
- **Test results** - JUnit XML

### **Notifications:**
- **Success**: Wszystkie testy przeszły, kod przeniesiony
- **Failure**: Szczegóły błędów, linki do logów

## 🚨 Troubleshooting

### **Typowe problemy:**

**1. Testy nie przechodzą:**
```bash
# Sprawdź lokalnie
./scripts/test-ci-cd.sh

# Sprawdź logi
tail -f logs/ci-cd-test.log
```

**2. Docker build fails:**
```bash
# Sprawdź Dockerfile
docker build -f Dockerfile.prod .

# Sprawdź Dockerfile.ui
docker build -f Dockerfile.ui .
```

**3. Transfer fails:**
```bash
# Sprawdź uprawnienia do target repo
# Sprawdź czy target repo istnieje
# Sprawdź czy nie ma konfliktów
```

**4. Timeout errors:**
```yaml
# Zwiększ timeout w workflow
timeout-minutes: 30
```

### **Debug workflow:**
```bash
# Włącz debug mode
echo "::debug::Debug message" >> $GITHUB_STEP_SUMMARY

# Sprawdź zmienne
echo "Repository: ${{ github.repository }}"
echo "Branch: ${{ github.ref }}"
```

## 🔐 Security

### **Secrets management:**
```yaml
# Użyj GitHub Secrets dla wrażliwych danych
env:
  SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
```

### **Permissions:**
```yaml
permissions:
  contents: write  # Do push do target repo
  actions: read    # Do odczytu workflow
```

## 📈 Metrics i Analytics

### **Codecov:**
- Pokrycie kodu w czasie
- Trendy jakości
- Raporty dla PR

### **GitHub Actions:**
- Czas wykonania pipeline
- Success rate
- Resource usage

## 🎯 Best Practices

### **1. Testuj lokalnie przed push:**
```bash
./scripts/test-ci-cd.sh
```

### **2. Używaj meaningful commit messages:**
```bash
git commit -m "feat: add new ML model support"
git commit -m "fix: resolve preprocessor loading issue"
```

### **3. Monitoruj pipeline:**
- Sprawdzaj GitHub Actions regularnie
- Reaguj na błędy szybko
- Analizuj metryki

### **4. Keep dependencies updated:**
```bash
# Regularnie aktualizuj zależności
pip install --upgrade -r requirements.txt
```

## 🔗 Przydatne linki

- **GitHub Actions**: https://github.com/features/actions
- **Codecov**: https://codecov.io/
- **Docker**: https://www.docker.com/
- **Bandit**: https://bandit.readthedocs.io/
- **Safety**: https://pyup.io/safety/

## 📞 Support

### **Gdzie szukać pomocy:**
1. **GitHub Issues** - zgłoś problemy z pipeline
2. **GitHub Actions logs** - szczegółowe logi błędów
3. **Local testing** - `./scripts/test-ci-cd.sh`
4. **Documentation** - ten przewodnik

### **Przykładowe problemy:**
- [Pipeline timeout](https://github.com/actions/runner/issues)
- [Docker build issues](https://docs.docker.com/engine/reference/builder/)
- [GitHub Actions permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)

---

**🚀 Happy deploying!** 🎉
