"""
Pytest configuration and common fixtures for the Intrusion Detector test suite.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from datetime import datetime


@pytest.fixture
def temp_file():
    """Provide a temporary file for testing file operations."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("test content")
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide a test data directory."""
    return os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture
def mock_openai_client():
    """Provide a mock OpenAI client for testing LLM functionality."""
    with patch("openai.OpenAI") as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_redis_client():
    """Provide a mock Redis client for testing cache functionality."""
    with patch("redis.Redis") as mock_redis:
        mock_instance = Mock()
        mock_redis.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_supabase_client():
    """Provide a mock Supabase client for testing database operations."""
    with patch("supabase.Client") as mock_supabase:
        mock_instance = Mock()
        mock_supabase.return_value = mock_instance
        yield mock_instance


# Custom markers for test categorization
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "e2e: mark test as an end-to-end test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "security: mark test as security-related")
    config.addinivalue_line("markers", "ml: mark test as machine learning related")
    config.addinivalue_line("markers", "api: mark test as API related")
    config.addinivalue_line("markers", "ui: mark test as UI related")


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add unit marker to tests in unit directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Add security marker to security-related tests
        if any(
            keyword in item.name.lower() for keyword in ["security", "auth", "threat"]
        ):
            item.add_marker(pytest.mark.security)

        # Add ml marker to ML-related tests
        if any(
            keyword in item.name.lower()
            for keyword in ["ml", "model", "preprocessor", "classification"]
        ):
            item.add_marker(pytest.mark.ml)

        # Add api marker to API-related tests
        if any(
            keyword in item.name.lower() for keyword in ["api", "endpoint", "route"]
        ):
            item.add_marker(pytest.mark.api)

        # Add ui marker to UI-related tests
        if any(
            keyword in item.name.lower() for keyword in ["ui", "gradio", "interface"]
        ):
            item.add_marker(pytest.mark.ui)
