from fastapi.testclient import TestClient
from app.main import app
from app.database import get_master_db
from app.services.org_service import OrgService

client = TestClient(app)


def teardown_module(module):
    """Clean up test data"""
    db = get_master_db()
    db["admins"].delete_many({"email": {"$regex": "test_"}})
    db["organizations"].delete_many({"name": {"$regex": "test_"}})


def test_admin_login_success():
    """Test successful admin login"""
    # Create org first
    org_name = "test_auth_org"
    email = "test_admin_auth@example.com"
    password = "testpass123"
    
    OrgService.create_org(org_name, email, password)
    
    # Test login
    response = client.post(
        "/admin/login",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_admin_login_wrong_password():
    """Test login with wrong password"""
    org_name = "test_auth_org2"
    email = "test_admin_auth2@example.com"
    password = "testpass123"
    
    OrgService.create_org(org_name, email, password)
    
    response = client.post(
        "/admin/login",
        json={"email": email, "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_admin_login_wrong_email():
    """Test login with non-existent email"""
    response = client.post(
        "/admin/login",
        json={"email": "nonexistent@example.com", "password": "password123"}
    )
    assert response.status_code == 401


def test_admin_login_missing_fields():
    """Test login with missing fields"""
    response = client.post(
        "/admin/login",
        json={"email": "test@example.com"}
    )
    assert response.status_code == 422


def test_admin_login_invalid_email():
    """Test login with invalid email format"""
    response = client.post(
        "/admin/login",
        json={"email": "invalid-email", "password": "password123"}
    )
    assert response.status_code == 422

