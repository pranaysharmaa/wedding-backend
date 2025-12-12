#!/usr/bin/env python3
"""
Comprehensive API test script for Wedding Backend
Tests endpoints, validation, database operations, and authentication
"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
test_results = []

def log_test(name, passed, message=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    result = f"{status}: {name}"
    if message:
        result += f" - {message}"
    print(result)
    test_results.append((name, passed, message))
    return passed

def print_section(title):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_root_endpoint():
    """Test root endpoint"""
    print_section("Testing Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/")
        log_test("Root endpoint accessible", response.status_code == 200)
        if response.status_code == 200:
            data = response.json()
            log_test("Root returns correct structure", "status" in data and "service" in data)
            print(f"   Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        log_test("Root endpoint accessible", False, str(e))
        return False
    return True

def test_validation():
    """Test input validation"""
    print_section("Testing Input Validation")
    
    # Test invalid email
    try:
        response = requests.post(f"{BASE_URL}/org/create", json={
            "organization_name": "TestOrg",
            "email": "invalid-email",
            "password": "password123"
        })
        log_test("Invalid email rejected", response.status_code == 422, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test("Invalid email rejected", False, str(e))
    
    # Test short password
    try:
        response = requests.post(f"{BASE_URL}/org/create", json={
            "organization_name": "TestOrg",
            "email": "test@example.com",
            "password": "short"
        })
        log_test("Short password rejected", response.status_code == 422,
                f"Status: {response.status_code}")
    except Exception as e:
        log_test("Short password rejected", False, str(e))
    
    # Test invalid org name (special characters)
    try:
        response = requests.post(f"{BASE_URL}/org/create", json={
            "organization_name": "Test@Org#Invalid",
            "email": "test@example.com",
            "password": "password123"
        })
        log_test("Invalid org name rejected", response.status_code == 422,
                f"Status: {response.status_code}")
    except Exception as e:
        log_test("Invalid org name rejected", False, str(e))
    
    # Test empty org name
    try:
        response = requests.post(f"{BASE_URL}/org/create", json={
            "organization_name": "",
            "email": "test@example.com",
            "password": "password123"
        })
        log_test("Empty org name rejected", response.status_code == 422,
                f"Status: {response.status_code}")
    except Exception as e:
        log_test("Empty org name rejected", False, str(e))
    
    # Test missing fields
    try:
        response = requests.post(f"{BASE_URL}/org/create", json={
            "organization_name": "TestOrg"
        })
        log_test("Missing fields rejected", response.status_code == 422,
                f"Status: {response.status_code}")
    except Exception as e:
        log_test("Missing fields rejected", False, str(e))

def test_org_creation():
    """Test organization creation and retrieval"""
    print_section("Testing Organization Creation")
    
    org_name = f"test_org_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    email = f"admin_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com"
    password = "testpass123"
    
    # Create organization
    try:
        response = requests.post(f"{BASE_URL}/org/create", json={
            "organization_name": org_name,
            "email": email,
            "password": password
        })
        passed = response.status_code == 201
        log_test("Organization creation", passed, 
                f"Status: {response.status_code}")
        
        if passed:
            data = response.json()
            log_test("Response contains required fields", 
                    "name" in data and "collection" in data and "admin_email" in data)
            log_test("Collection name format correct", 
                    data["collection"].startswith("org_"))
            log_test("Admin email matches", data["admin_email"] == email)
            print(f"   Created org: {json.dumps(data, indent=2)}")
            
            # Test retrieval
            response2 = requests.get(f"{BASE_URL}/org/get", 
                                    params={"organization_name": org_name})
            passed2 = response2.status_code == 200
            log_test("Organization retrieval", passed2,
                    f"Status: {response2.status_code}")
            
            if passed2:
                data2 = response2.json()
                log_test("Retrieved org matches created", 
                        data2["name"] == org_name and data2["admin_email"] == email)
                print(f"   Retrieved org: {json.dumps(data2, indent=2)}")
            
            return org_name, email, password
        else:
            print(f"   Error: {response.text}")
            return None, None, None
    except Exception as e:
        log_test("Organization creation", False, str(e))
        return None, None, None

def test_duplicate_org():
    """Test duplicate organization creation"""
    print_section("Testing Duplicate Organization Prevention")
    
    org_name = f"duplicate_test_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    email1 = f"admin1_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com"
    email2 = f"admin2_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com"
    
    # Create first org
    try:
        response1 = requests.post(f"{BASE_URL}/org/create", json={
            "organization_name": org_name,
            "email": email1,
            "password": "password123"
        })
        if response1.status_code == 201:
            # Try to create duplicate
            response2 = requests.post(f"{BASE_URL}/org/create", json={
                "organization_name": org_name,
                "email": email2,
                "password": "password123"
            })
            log_test("Duplicate org name rejected", response2.status_code == 400,
                    f"Status: {response2.status_code}")
            
            # Try duplicate email
            response3 = requests.post(f"{BASE_URL}/org/create", json={
                "organization_name": f"{org_name}_different",
                "email": email1,  # Same email
                "password": "password123"
            })
            log_test("Duplicate email rejected", response3.status_code == 400,
                    f"Status: {response3.status_code}")
    except Exception as e:
        log_test("Duplicate org prevention", False, str(e))

def test_authentication():
    """Test admin authentication"""
    print_section("Testing Authentication")
    
    org_name = f"auth_test_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    email = f"auth_admin_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com"
    password = "authpass123"
    
    # Create org first
    try:
        create_resp = requests.post(f"{BASE_URL}/org/create", json={
            "organization_name": org_name,
            "email": email,
            "password": password
        })
        
        if create_resp.status_code != 201:
            log_test("Auth test setup", False, "Failed to create org for auth test")
            return None, None
        
        # Test successful login
        login_resp = requests.post(f"{BASE_URL}/admin/login", json={
            "email": email,
            "password": password
        })
        passed = login_resp.status_code == 200
        log_test("Successful login", passed, f"Status: {login_resp.status_code}")
        
        if passed:
            token_data = login_resp.json()
            log_test("Token response structure", 
                    "access_token" in token_data and "token_type" in token_data)
            log_test("Token type is bearer", token_data.get("token_type") == "bearer")
            token = token_data.get("access_token")
            print(f"   Token received: {token[:50]}...")
            
            # Test failed login (wrong password)
            fail_resp = requests.post(f"{BASE_URL}/admin/login", json={
                "email": email,
                "password": "wrongpassword"
            })
            log_test("Wrong password rejected", fail_resp.status_code in [401, 400],
                    f"Status: {fail_resp.status_code}")
            
            # Test failed login (wrong email)
            fail_resp2 = requests.post(f"{BASE_URL}/admin/login", json={
                "email": "nonexistent@test.com",
                "password": password
            })
            log_test("Wrong email rejected", fail_resp2.status_code in [401, 400],
                    f"Status: {fail_resp2.status_code}")
            
            return org_name, token
        else:
            print(f"   Login error: {login_resp.text}")
            return None, None
    except Exception as e:
        log_test("Authentication", False, str(e))
        return None, None

def test_protected_endpoints():
    """Test protected endpoints with authentication"""
    print_section("Testing Protected Endpoints")
    
    org_name, token = test_authentication()
    if not org_name or not token:
        log_test("Protected endpoints test", False, "Auth setup failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test update org (requires auth)
    try:
        new_name = f"{org_name}_updated"
        update_resp = requests.put(
            f"{BASE_URL}/org/update",
            params={"current_name": org_name, "new_name": new_name},
            headers=headers
        )
        passed = update_resp.status_code == 200
        log_test("Update org with auth", passed, f"Status: {update_resp.status_code}")
        
        if passed:
            data = update_resp.json()
            log_test("Update response structure", "new_name" in data)
            print(f"   Updated org: {json.dumps(data, indent=2)}")
            
            # Verify update
            get_resp = requests.get(f"{BASE_URL}/org/get",
                                   params={"organization_name": new_name})
            log_test("Updated org retrievable", get_resp.status_code == 200)
            
            org_name = new_name  # Update for delete test
    except Exception as e:
        log_test("Update org", False, str(e))
    
    # Test delete org (requires auth)
    try:
        delete_resp = requests.delete(
            f"{BASE_URL}/org/delete",
            params={"org_name": org_name},
            headers=headers
        )
        passed = delete_resp.status_code == 200
        log_test("Delete org with auth", passed, f"Status: {delete_resp.status_code}")
        
        if passed:
            # Verify deletion
            get_resp = requests.get(f"{BASE_URL}/org/get",
                                   params={"organization_name": org_name})
            log_test("Deleted org not retrievable", get_resp.status_code == 404)
    except Exception as e:
        log_test("Delete org", False, str(e))
    
    # Test protected endpoint without auth
    try:
        no_auth_resp = requests.put(
            f"{BASE_URL}/org/update",
            params={"current_name": "test", "new_name": "test2"}
        )
        log_test("Protected endpoint without auth rejected", 
                no_auth_resp.status_code == 401,
                f"Status: {no_auth_resp.status_code}")
    except Exception as e:
        log_test("Auth check", False, str(e))

def test_nonexistent_org():
    """Test operations on nonexistent organization"""
    print_section("Testing Nonexistent Organization Handling")
    
    try:
        response = requests.get(f"{BASE_URL}/org/get",
                               params={"organization_name": "nonexistent_org_xyz123"})
        log_test("Nonexistent org returns 404", response.status_code == 404,
                f"Status: {response.status_code}")
    except Exception as e:
        log_test("Nonexistent org handling", False, str(e))

def test_database_persistence():
    """Test that data persists in database"""
    print_section("Testing Database Persistence")
    
    org_name = f"persist_test_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    email = f"persist_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com"
    
    try:
        # Create org
        create_resp = requests.post(f"{BASE_URL}/org/create", json={
            "organization_name": org_name,
            "email": email,
            "password": "password123"
        })
        
        if create_resp.status_code == 201:
            # Wait a moment
            import time
            time.sleep(1)
            
            # Retrieve it
            get_resp = requests.get(f"{BASE_URL}/org/get",
                                   params={"organization_name": org_name})
            log_test("Data persists in database", get_resp.status_code == 200,
                    "Org retrievable after creation")
            
            if get_resp.status_code == 200:
                data = get_resp.json()
                log_test("Persisted data is correct", 
                        data["name"] == org_name and data["admin_email"] == email)
    except Exception as e:
        log_test("Database persistence", False, str(e))

def print_summary():
    """Print test summary"""
    print_section("Test Summary")
    total = len(test_results)
    passed = sum(1 for _, p, _ in test_results if p)
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if failed > 0:
        print("\nFailed Tests:")
        for name, passed, message in test_results:
            if not passed:
                print(f"  - {name}: {message}")
    
    return failed == 0

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  WEDDING BACKEND API TEST SUITE")
    print("="*60)
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/", timeout=5)
    except Exception as e:
        print(f"\n❌ ERROR: Cannot connect to {BASE_URL}")
        print(f"   Make sure the server is running: docker-compose up")
        sys.exit(1)
    
    # Run tests
    test_root_endpoint()
    test_validation()
    test_org_creation()
    test_duplicate_org()
    test_authentication()
    test_protected_endpoints()
    test_nonexistent_org()
    test_database_persistence()
    
    # Print summary
    success = print_summary()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

