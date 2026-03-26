"""
Pytest configuration and fixtures for the test suite
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture(scope="function")
def test_client():
    """Provide a test client for API testing"""
    return TestClient(app)
