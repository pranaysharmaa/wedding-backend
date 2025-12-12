"""
Pytest configuration and fixtures for tests.
"""
import pytest
from app.database import get_client


@pytest.fixture(scope="session", autouse=True)
def check_db_connection():
    """Check database connection at the start of test session."""
    try:
        client = get_client()
        client.admin.command("ping")
    except Exception as e:
        # Log warning but don't skip - let individual tests handle it
        print(f"Warning: MongoDB connection check failed: {e}")
        print("Tests will attempt to connect individually")

