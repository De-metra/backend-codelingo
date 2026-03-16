import pytest

from app.core.security import get_password_hash, verify_password, create_jwt_token


def test_password_hashing():
    password = "secret password"
    password_hash = get_password_hash(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True
    assert verify_password("wrong password", password_hash) is False

# def test_create_jwt():    # false
#     data = {"sub": "1"}
    
#     token1 = create_jwt_token(data)
#     token2 = create_jwt_token(data)

#     assert token1 != token2