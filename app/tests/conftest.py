"""
Pytest configuration and fixtures for tests.
"""
import pytest
from app.database import get_client


@pytest.fixture(autouse=True)
def ensure_db_connection():
    """Ensure database connection is available before each test."""
    try:
        client = get_client()
        client.admin.command("ping")
    except Exception as e:
        pytest.skip(f"MongoDB not available: {e}")

