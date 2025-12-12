from fastapi.testclient import TestClient
from app.main import app
from app.database import get_master_db, tenant_collection_name, delete_tenant_collection

client = TestClient(app)


def teardown_module(module):
    # clean test org collections from master_db to avoid pollution
    db = get_master_db()
    # remove test entries if exist
    db["admins"].delete_many({"email": {"$regex": "test_admin"}})
    db["organizations"].delete_many({"name": {"$regex": "test_org"}})
    # drop tenant collection if exists
    try:
        delete_tenant_collection("test_org")
    except Exception:
        pass


def test_create_and_get_org():
    payload = {
        "organization_name": "test_org",
        "email": "test_admin@example.com",
        "password": "testpass123"
    }
    res = client.post("/org/create", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "test_org"
    assert data["collection"].startswith("org_")
    # get
    res2 = client.get("/org/get", params={"organization_name": "test_org"})
    assert res2.status_code == 200
    g = res2.json()
    assert g["name"] == "test_org"
