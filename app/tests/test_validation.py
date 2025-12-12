from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_org_invalid_email():
    """Test organization creation with invalid email"""
    response = client.post(
        "/org/create",
        json={
            "organization_name": "TestOrg",
            "email": "invalid-email",
            "password": "password123"
        }
    )
    assert response.status_code == 422


def test_create_org_short_password():
    """Test organization creation with short password"""
    response = client.post(
        "/org/create",
        json={
            "organization_name": "TestOrg",
            "email": "test@example.com",
            "password": "short"
        }
    )
    assert response.status_code == 422


def test_create_org_invalid_org_name():
    """Test organization creation with invalid org name"""
    response = client.post(
        "/org/create",
        json={
            "organization_name": "Test@Org#Invalid",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 422


def test_create_org_empty_name():
    """Test organization creation with empty name"""
    response = client.post(
        "/org/create",
        json={
            "organization_name": "",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 422


def test_create_org_missing_fields():
    """Test organization creation with missing fields"""
    response = client.post(
        "/org/create",
        json={
            "organization_name": "TestOrg"
        }
    )
    assert response.status_code == 422

