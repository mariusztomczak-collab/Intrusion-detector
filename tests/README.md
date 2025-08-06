# Test Suite Documentation

## Overview

This directory contains the comprehensive test suite for the Intrusion Detection System. The tests are organized to ensure high code coverage and reliability across all components.

## Test Structure

```
tests/
├── unit/                          # Unit tests for individual components
│   ├── test_api.py               # FastAPI application tests
│   ├── test_auth.py              # Authentication logic tests
│   ├── test_database.py          # Database operations tests
│   ├── test_preprocessor.py      # ML preprocessor tests
│   └── test_ui_components.py     # Gradio UI component tests
├── conftest.py                   # Pytest fixtures and configuration
├── pytest.ini                   # Pytest configuration
└── README.md                     # This file
```

## Running Tests

### Run All Tests
```bash
pytest tests/unit/
```

### Run Specific Test Files
```bash
pytest tests/unit/test_api.py
pytest tests/unit/test_auth.py
pytest tests/unit/test_database.py
pytest tests/unit/test_preprocessor.py
pytest tests/unit/test_ui_components.py
```

### Run with Coverage
```bash
pytest tests/unit/ --cov=src --cov-report=term-missing
```

### Run with HTML Coverage Report
```bash
pytest tests/unit/ --cov=src --cov-report=html
```

### Filter Tests by Markers
```bash
pytest -m unit          # Run only unit tests
pytest -m api           # Run API-related tests
pytest -m auth          # Run authentication tests
pytest -m database      # Run database tests
pytest -m ml            # Run ML-related tests
pytest -m ui            # Run UI tests
```

## Test Categories

### Unit Tests (`tests/unit/`)

#### API Tests (`test_api.py`)
- **Health Check Endpoint**: Tests the `/health` endpoint
- **Root Endpoint**: Tests the `/` endpoint
- **Authentication Endpoints**: Tests `/auth/register` and `/auth/login`
- **Decision Endpoints**: Tests `/decisions/single` and `/decisions/`
- **Error Handling**: Tests various error scenarios

#### Authentication Tests (`test_auth.py`)
- **Email Validation**: Tests email format validation
- **Login Success/Failure**: Tests login with valid/invalid credentials
- **Registration**: Tests user registration process
- **Error Messages**: Tests error message display

#### Database Tests (`test_database.py`)
- **Supabase Client**: Tests Supabase client operations
- **Redis Client**: Tests Redis cache operations
- **Data Validation**: Tests Pydantic model validation
- **Error Handling**: Tests database error scenarios

#### ML Preprocessor Tests (`test_preprocessor.py`)
- **Initialization**: Tests DataPreprocessor setup
- **Data Transformation**: Tests feature scaling and encoding
- **Edge Cases**: Tests missing values, invalid data types
- **Integration**: Tests with realistic traffic data

#### UI Component Tests (`test_ui_components.py`)
- **App Initialization**: Tests UnifiedApp setup
- **Email Validation**: Tests email format validation in UI
- **Login Handling**: Tests login success/failure scenarios
- **Registration**: Tests user registration in UI
- **Logout**: Tests logout functionality

## Test Configuration

### pytest.ini
- **Test Discovery**: Configures test file patterns
- **Markers**: Defines custom test markers for categorization
- **Coverage**: Configures coverage reporting
- **Warnings**: Suppresses known deprecation warnings

### conftest.py
- **Fixtures**: Provides common test fixtures
- **Mocking**: Sets up mock objects for external dependencies
- **Test Data**: Provides sample data for tests
- **Configuration**: Sets up test environment

## Test Markers

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.api`: API-related tests
- `@pytest.mark.auth`: Authentication tests
- `@pytest.mark.database`: Database tests
- `@pytest.mark.ml`: Machine learning tests
- `@pytest.mark.ui`: User interface tests
- `@pytest.mark.security`: Security-related tests

## Coverage Goals

- **Overall Coverage**: Target 80%+
- **Critical Components**: 90%+ (API, Auth, Database)
- **UI Components**: 70%+ (Gradio interface)
- **ML Components**: 85%+ (Preprocessor, Models)

## Current Status

### Test Results
- **Total Tests**: 53
- **Passed**: 53 (100%)
- **Failed**: 0 (0%)
- **Coverage**: 50%

### Component Coverage
- **API Layer**: 34% (needs improvement)
- **Authentication**: 71% (good)
- **Database**: 39% (needs improvement)
- **ML Preprocessor**: 92% (excellent)
- **UI Components**: 38% (needs improvement)

## Quality Checklist

### ✅ Implemented
- [x] Unit tests for all major components
- [x] API endpoint testing
- [x] Authentication flow testing
- [x] Database operation testing
- [x] ML preprocessor testing
- [x] UI component testing
- [x] Error handling tests
- [x] Mock external dependencies
- [x] Coverage reporting
- [x] Test categorization with markers

### 🔄 To Be Implemented
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] Performance tests
- [ ] Security tests
- [ ] Load testing
- [ ] API contract testing

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Mocking**: Use mocks for external dependencies
3. **Descriptive Names**: Test names should clearly describe what they test
4. **Arrange-Act-Assert**: Follow the AAA pattern
5. **Edge Cases**: Test boundary conditions and error scenarios
6. **Coverage**: Aim for high coverage but focus on critical paths

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure virtual environment is activated
2. **Mock Issues**: Check mock setup in conftest.py
3. **Database Errors**: Ensure test database is properly configured
4. **Coverage Issues**: Check that all source files are included

### Debugging
```bash
# Run tests with verbose output
pytest -v tests/unit/

# Run specific test with detailed output
pytest -vvv tests/unit/test_api.py::TestAPIEndpoints::test_health_check

# Run tests with print statements
pytest -s tests/unit/
```

## Contributing

When adding new tests:
1. Follow the existing naming conventions
2. Add appropriate markers
3. Include docstrings
4. Test both success and failure scenarios
5. Update this documentation if needed 