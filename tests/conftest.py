import pytest

@pytest.fixture
def db_session():
    return {"connected": True}
