from fastapi.testclient import TestClient
from app.main import app
from app.database import get_master_db
from app.services.org_service import OrgService

client = TestClient(app)


def teardown_module(module):
    """Clean up test data"""
    try:
        db = get_master_db()
        db["admins"].delete_many({"email": {"$regex": "test_protected"}})
        db["organizations"].delete_many({"name": {"$regex": "test_protected"}})
    except Exception:
        # Ignore cleanup errors
        pass


def test_update_org_without_auth():
    """Test updating org without authentication"""
    response = client.put(
        "/org/update?current_name=test&new_name=test2"
    )
    assert response.status_code == 401


def test_delete_org_without_auth():
    """Test deleting org without authentication"""
    response = client.delete(
        "/org/delete?org_name=test"
    )
    assert response.status_code == 401


def test_update_org_with_auth():
    """Test updating org with valid authentication"""
    # Create org
    org_name = "test_protected_org"
    email = "test_protected@example.com"
    password = "testpass123"
    
    OrgService.create_org(org_name, email, password)
    
    # Login to get token
    login_response = client.post(
        "/admin/login",
        json={"email": email, "password": password}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Update org
    new_name = "test_protected_org_updated"
    response = client.put(
        f"/org/update?current_name={org_name}&new_name={new_name}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Verify update
    get_response = client.get(f"/org/get?organization_name={new_name}")
    assert get_response.status_code == 200


def test_delete_org_with_auth():
    """Test deleting org with valid authentication"""
    # Create org
    org_name = "test_protected_delete"
    email = "test_protected_delete@example.com"
    password = "testpass123"
    
    OrgService.create_org(org_name, email, password)
    
    # Login to get token
    login_response = client.post(
        "/admin/login",
        json={"email": email, "password": password}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Delete org
    response = client.delete(
        f"/org/delete?org_name={org_name}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Verify deletion
    get_response = client.get(f"/org/get?organization_name={org_name}")
    assert get_response.status_code == 404

