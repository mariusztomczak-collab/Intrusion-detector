#!/usr/bin/env python3
"""
Unit tests for CI/CD workflow verification.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ci_cd_test import verify_ci_cd_function, main


def test_ci_cd_function_returns_true():
    """Test that the CI/CD function returns True."""
    result = verify_ci_cd_function()
    assert result is True


def test_main_function_returns_zero():
    """Test that the main function returns 0 (success)."""
    result = main()
    assert result == 0


def test_ci_cd_function_output(capsys):
    """Test that the CI/CD function prints the expected output."""
    verify_ci_cd_function()
    captured = capsys.readouterr()
    assert "✅ CI/CD workflow test function executed successfully!" in captured.out


def test_main_function_output(capsys):
    """Test that the main function prints the expected output."""
    main()
    captured = capsys.readouterr()
    assert "🚀 Testing CI/CD Workflow" in captured.out
    assert "✅ All tests passed!" in captured.out 