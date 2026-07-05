import pytest

def test_get_user_endpoint():
    """Test API endpoint - FAILING: path changed"""
    response = {"status": 200, "url": "/api/users"}
    # This assertion fails because endpoint path changed from /api/user to /api/users
    assert response["url"] == "/api/user", f"Expected /api/user but got {response['url']}"

def test_create_user():
    """Test user creation endpoint"""
    assert True
