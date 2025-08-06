# GitHub Actions CI/CD Workflow Documentation

## Overview

This directory contains GitHub Actions workflows for the Intrusion Detector project.

## Workflows

### `pull-request.yml`

**Purpose**: Comprehensive CI/CD pipeline for pull requests

**Triggers**:
- Pull requests to `main` or `master` branches
- Events: `opened`, `synchronize`, `reopened`

## Job Structure

### 1. **Lint** (Code Quality & Linting)
- **Duration**: ~10 minutes
- **Tools**:
  - **Black**: Code formatting check
  - **isort**: Import sorting check
  - **flake8**: Code quality check
  - **mypy**: Type checking

### 2. **Unit Tests** (Parallel Matrix)
- **Duration**: ~15 minutes
- **Strategy**: Matrix with test suites (`api`, `ml`, `ui`, `core`)
- **Features**:
  - Coverage collection (XML, HTML, terminal)
  - Codecov integration
  - JUnit XML reports
  - Parallel execution

### 3. **Integration Tests**
- **Duration**: ~20 minutes
- **Dependencies**: Requires `lint` and `unit-tests` to pass
- **Features**:
  - End-to-end testing
  - Coverage collection
  - JUnit XML reports

### 4. **Security Scan**
- **Duration**: ~10 minutes
- **Tools**:
  - **Bandit**: Python security scanner
  - **Safety**: Dependency vulnerability check
- **Output**: Security reports as artifacts

### 5. **Build Docker Images**
- **Duration**: ~15 minutes
- **Dependencies**: Requires `lint` and `unit-tests` to pass
- **Images**:
  - API: `Dockerfile.prod`
  - UI: `Dockerfile.ui`
- **Features**: Image testing and validation

### 6. **Status Comment**
- **Duration**: ~2 minutes
- **Dependencies**: All previous jobs
- **Features**:
  - Automatic PR comment with status report
  - Coverage links
  - Next steps guidance
  - Updates existing comments

## Environment Configuration

### Python Environment
- **Version**: 3.12
- **Cache**: pip dependencies
- **Installation**: `pip install -e ".[dev]"`

### System Dependencies
- **Redis**: For caching tests
- **PostgreSQL Client**: For database tests
- **Docker**: For image building

### Environment Variables
```bash
MLFLOW_TRACKING_URI=local
SUPABASE_URL=http://localhost:54321
SUPABASE_KEY=test-key
REDIS_URL=redis://localhost:6379
```

## Coverage Collection

### Reports Generated
- **XML**: For Codecov integration
- **HTML**: For detailed coverage analysis
- **Terminal**: For immediate feedback

### Coverage Provider
- **Codecov**: For coverage trends and reports
- **Flags**: `unittests`, `integration`

## Artifacts

### Test Results
- JUnit XML reports for each test suite
- Coverage reports (HTML, XML)
- Security scan reports

### Docker Images
- Built and tested Docker images
- Tagged with PR number for identification

## Status Comment Format

The workflow generates a comprehensive status comment with:

```markdown
## 🎉 Pull Request CI/CD Status Report

### Overall Status: ✅ All checks passed

| Check | Status |
|-------|--------|
| Code Linting | ✅ Passed |
| Unit Tests | ✅ Passed |
| Integration Tests | ✅ Passed |
| Security Scan | ✅ Passed |
| Docker Build | ✅ Passed |

### Coverage Report
- Unit tests coverage: [View Coverage Report](https://codecov.io/...)

### Next Steps
- ✅ Ready for review and merge

---
*This report was generated automatically by GitHub Actions*
```

## Dependencies

### Required Python Packages
```toml
[project.dependencies]
fastapi = ">=0.109.0"
uvicorn = ">=0.27.0"
pydantic = ">=2.4.2"
supabase = ">=2.3.0"
mlflow = ">=2.10.0"
scikit-learn = ">=1.4.0"
pandas = ">=2.2.0"
numpy = ">=1.26.0"
redis = ">=4.2.0,<5.0.0"

[project.optional-dependencies]
dev = [
    "pytest>=7.4.3",
    "pytest-cov>=4.1.0",
    "black>=23.11.0",
    "isort>=5.12.0",
    "flake8>=6.1.0",
    "mypy>=1.7.1",
]
```

## Troubleshooting

### Common Issues

1. **Linting Failures**
   - Run `black src/ tests/` to format code
   - Run `isort src/ tests/` to sort imports
   - Fix flake8 warnings

2. **Test Failures**
   - Check test logs for specific failures
   - Ensure sample model is created: `python scripts/create_sample_model.py`
   - Verify environment variables are set

3. **Docker Build Failures**
   - Check Dockerfile syntax
   - Verify all required files are present
   - Check for missing dependencies

4. **Security Scan Failures**
   - Review Bandit warnings
   - Update vulnerable dependencies
   - Address security concerns

### Local Testing

To test the workflow locally:

```bash
# Install dependencies
pip install -e ".[dev]"

# Run linting
black --check src/ tests/
isort --check-only src/ tests/
flake8 src/ tests/
mypy src/

# Run tests
pytest tests/ --cov=src --cov-report=html

# Create sample model
python scripts/create_sample_model.py

# Build Docker images
docker build -f Dockerfile.prod -t test-api .
docker build -f Dockerfile.ui -t test-ui .
```

## Performance Optimization

### Caching Strategy
- **pip**: Cached dependencies
- **Docker**: Layer caching for images
- **Test results**: Cached between runs

### Parallel Execution
- Unit tests run in parallel matrix
- Independent jobs run concurrently
- Optimized job dependencies

### Timeout Settings
- Lint: 10 minutes
- Unit Tests: 15 minutes
- Integration Tests: 20 minutes
- Security Scan: 10 minutes
- Docker Build: 15 minutes
- Status Comment: 2 minutes 