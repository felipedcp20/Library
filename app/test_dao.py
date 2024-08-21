import pytest
from unittest.mock import MagicMock
from app.dao import Dao

def test_get_user():
    client = Dao()
    user = client.get_user("mock")
    assert user is not None
    assert user.username == "mock"

