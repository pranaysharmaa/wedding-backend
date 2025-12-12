#!/bin/bash
# Comprehensive API test script using curl

BASE_URL="http://localhost:8000"
PASSED=0
FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_section() {
    echo ""
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

test_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASSED++))
}

test_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1 - $2"
    ((FAILED++))
}

test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local expected_status=$4
    local data=$5
    local headers=$6
    
    # Build curl command
    local curl_args=(-s -w "\n%{http_code}" -H "Content-Type: application/json")
    
    # Add additional headers if provided (format: "Header1: value1\nHeader2: value2")
    if [ -n "$headers" ]; then
        while IFS= read -r header; do
            if [ -n "$header" ]; then
                curl_args+=(-H "$header")
            fi
        done <<< "$headers"
    fi
    
    if [ "$method" = "GET" ]; then
        response=$(curl "${curl_args[@]}" "$url")
    else
        response=$(curl "${curl_args[@]}" -X "$method" -d "$data" "$url")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
        test_pass "$name"
        if [ -n "$body" ] && [ "$body" != "null" ]; then
            echo "   Response: $(echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body")"
        fi
        return 0
    else
        test_fail "$name" "Expected $expected_status, got $http_code. Response: $body"
        return 1
    fi
}

# Test 1: Root endpoint
print_section "Testing Root Endpoint"
test_endpoint "Root endpoint accessible" "GET" "$BASE_URL/" "200"

# Test 2: Validation tests
print_section "Testing Input Validation"

# Invalid email
test_endpoint "Invalid email rejected" "POST" "$BASE_URL/org/create" "422" \
    '{"organization_name":"TestOrg","email":"invalid-email","password":"password123"}'

# Short password
test_endpoint "Short password rejected" "POST" "$BASE_URL/org/create" "422" \
    '{"organization_name":"TestOrg","email":"test@example.com","password":"short"}'

# Invalid org name (special chars)
test_endpoint "Invalid org name rejected" "POST" "$BASE_URL/org/create" "422" \
    '{"organization_name":"Test@Org#Invalid","email":"test@example.com","password":"password123"}'

# Empty org name
test_endpoint "Empty org name rejected" "POST" "$BASE_URL/org/create" "422" \
    '{"organization_name":"","email":"test@example.com","password":"password123"}'

# Missing fields
test_endpoint "Missing fields rejected" "POST" "$BASE_URL/org/create" "422" \
    '{"organization_name":"TestOrg"}'

# Test 3: Organization creation
print_section "Testing Organization Creation"

TIMESTAMP=$(date +%s)
ORG_NAME="test_org_$TIMESTAMP"
EMAIL="admin_$TIMESTAMP@test.com"
PASSWORD="testpass123"

# Create organization
if test_endpoint "Organization creation" "POST" "$BASE_URL/org/create" "201" \
    "{\"organization_name\":\"$ORG_NAME\",\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}"; then
    
    # Test retrieval
    test_endpoint "Organization retrieval" "GET" "$BASE_URL/org/get?organization_name=$ORG_NAME" "200"
fi

# Test 4: Duplicate prevention
print_section "Testing Duplicate Organization Prevention"

DUPLICATE_ORG="duplicate_test_$TIMESTAMP"
EMAIL1="admin1_$TIMESTAMP@test.com"
EMAIL2="admin2_$TIMESTAMP@test.com"

# Create first org
if test_endpoint "Create first org" "POST" "$BASE_URL/org/create" "201" \
    "{\"organization_name\":\"$DUPLICATE_ORG\",\"email\":\"$EMAIL1\",\"password\":\"password123\"}"; then
    
    # Try duplicate name
    test_endpoint "Duplicate org name rejected" "POST" "$BASE_URL/org/create" "400" \
        "{\"organization_name\":\"$DUPLICATE_ORG\",\"email\":\"$EMAIL2\",\"password\":\"password123\"}"
    
    # Try duplicate email
    test_endpoint "Duplicate email rejected" "POST" "$BASE_URL/org/create" "400" \
        "{\"organization_name\":\"${DUPLICATE_ORG}_different\",\"email\":\"$EMAIL1\",\"password\":\"password123\"}"
fi

# Test 5: Authentication
print_section "Testing Authentication"

AUTH_ORG="auth_test_$TIMESTAMP"
AUTH_EMAIL="auth_admin_$TIMESTAMP@test.com"
AUTH_PASSWORD="authpass123"

# Create org for auth test
if test_endpoint "Create org for auth test" "POST" "$BASE_URL/org/create" "201" \
    "{\"organization_name\":\"$AUTH_ORG\",\"email\":\"$AUTH_EMAIL\",\"password\":\"$AUTH_PASSWORD\"}"; then
    
    # Test successful login
    if test_endpoint "Successful login" "POST" "$BASE_URL/admin/login" "200" \
        "{\"email\":\"$AUTH_EMAIL\",\"password\":\"$AUTH_PASSWORD\"}"; then
        
        # Extract token (simplified - in real test we'd parse JSON)
        TOKEN_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
            -d "{\"email\":\"$AUTH_EMAIL\",\"password\":\"$AUTH_PASSWORD\"}" \
            "$BASE_URL/admin/login")
        
        TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)
        
        if [ -n "$TOKEN" ]; then
            echo "   Token received: ${TOKEN:0:50}..."
            
            # Test wrong password (401 is correct for authentication failures)
            test_endpoint "Wrong password rejected" "POST" "$BASE_URL/admin/login" "401" \
                "{\"email\":\"$AUTH_EMAIL\",\"password\":\"wrongpassword\"}"
            
            # Test wrong email (401 is correct for authentication failures)
            test_endpoint "Wrong email rejected" "POST" "$BASE_URL/admin/login" "401" \
                "{\"email\":\"nonexistent@test.com\",\"password\":\"$AUTH_PASSWORD\"}"
            
            # Test protected endpoints
            print_section "Testing Protected Endpoints"
            
            # Test update org with auth
            NEW_NAME="${AUTH_ORG}_updated"
            if test_endpoint "Update org with auth" "PUT" "$BASE_URL/org/update?current_name=$AUTH_ORG&new_name=$NEW_NAME" "200" "" \
                "Authorization: Bearer $TOKEN"; then
                
                # Verify update
                test_endpoint "Updated org retrievable" "GET" "$BASE_URL/org/get?organization_name=$NEW_NAME" "200"
                AUTH_ORG=$NEW_NAME
                
                # Get a new token after org name update (token contains old org name)
                TOKEN_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
                    -d "{\"email\":\"$AUTH_EMAIL\",\"password\":\"$AUTH_PASSWORD\"}" \
                    "$BASE_URL/admin/login")
                TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)
            fi
            
            # Test delete org with auth (use updated token)
            if [ -n "$TOKEN" ]; then
                test_endpoint "Delete org with auth" "DELETE" "$BASE_URL/org/delete?org_name=$AUTH_ORG" "200" "" \
                    "Authorization: Bearer $TOKEN"
            fi
            
            # Verify deletion
            test_endpoint "Deleted org not retrievable" "GET" "$BASE_URL/org/get?organization_name=$AUTH_ORG" "404"
            
            # Test protected endpoint without auth
            test_endpoint "Protected endpoint without auth rejected" "PUT" \
                "$BASE_URL/org/update?current_name=test&new_name=test2" "401" ""
        fi
    fi
fi

# Test 6: Nonexistent org
print_section "Testing Nonexistent Organization Handling"
test_endpoint "Nonexistent org returns 404" "GET" \
    "$BASE_URL/org/get?organization_name=nonexistent_org_xyz123" "404"

# Test 7: Database persistence
print_section "Testing Database Persistence"

PERSIST_ORG="persist_test_$TIMESTAMP"
PERSIST_EMAIL="persist_$TIMESTAMP@test.com"

if test_endpoint "Create org for persistence test" "POST" "$BASE_URL/org/create" "201" \
    "{\"organization_name\":\"$PERSIST_ORG\",\"email\":\"$PERSIST_EMAIL\",\"password\":\"password123\"}"; then
    
    sleep 1
    test_endpoint "Data persists in database" "GET" "$BASE_URL/org/get?organization_name=$PERSIST_ORG" "200"
fi

# Summary
print_section "Test Summary"
TOTAL=$((PASSED + FAILED))
echo "Total Tests: $TOTAL"
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"

if [ $TOTAL -gt 0 ]; then
    SUCCESS_RATE=$(echo "scale=1; $PASSED * 100 / $TOTAL" | bc)
    echo "Success Rate: ${SUCCESS_RATE}%"
fi

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed.${NC}"
    exit 1
fi

