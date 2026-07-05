"""测试用户模块"""

def get_new_user(name: str) -> dict:
    """模拟创建用户（新版本默认状态改为 'pending'）"""
    return {"name": name, "status": "pending"}

def test_user_creation():
    """Test user creation - FAILING: default status changed from 'active' to 'pending'"""
    user = get_new_user("Alice")
    # Old test expected 'active' but new default is 'pending'
    assert user["status"] == "active", f"Expected 'active' but got '{user['status']}'"

def test_user_deletion():
    """Test user deletion"""
    assert True
