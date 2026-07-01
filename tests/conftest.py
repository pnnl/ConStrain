"""
Pytest configuration file to ensure tests run with correct working directory
"""

import os
import sys
import pytest

# Get the project root directory (parent of tests directory, where pyproject.toml is)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="session", autouse=True)
def change_test_dir():
    """Change to project root directory before running tests"""
    os.chdir(PROJECT_ROOT)
    # Ensure project root is in Python path
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    yield
