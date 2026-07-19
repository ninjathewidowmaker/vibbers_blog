import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

import pytest
from datetime import timedelta
import jwt
import auth
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
import helfun

# Just getting our secret from env or using a dummy one for testing
SECRET_KEY = os.getenv('SECRET_KEY', 'dummy_secret')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')

@pytest.fixture
def anyio_backend():
    return 'asyncio'

def test_password_hashing():
    '''Let's see if the hash is actually hashing or just giving back plain text LOL'''
    password = "super_secret_password"
    hashed = auth.get_hash_pswd(password)
    
    # It shouldn't be the same, obviously
    assert hashed != password
    
    # Let's verify it with the right password
    magma = auth.verify_password(password, hashed)
    assert magma is True
    
    # Let's verify it with a wrong password
    gama = auth.verify_password("wrong_password", hashed)
    assert gama is False


def test_create_access_token():
    """
    Send data get a JWT token. Making sure it actually returns a string.
    """
    jama = {"username": "ninjathewidowmaker"}
    token = auth.create_access_token(data=jama, expires_delta=timedelta(minutes=15))
    
    assert isinstance(token, str)
    assert len(token) > 20 # just ensuring it's not some empty bs


def test_verify_access_token_valid():
    "Pass the JWT token to check if the token is valid or not"
    jama = {"username": "test_user"}
    token = auth.create_access_token(data=jama)
    
    # Let's see if we get our payload back
    confirm = auth.verify_access_token(token)
    
    assert confirm is not None
    assert confirm.get("username") == "test_user"
    assert "exp" in confirm


def test_verify_access_token_invalid():
    '''Testing a deadass wrong token'''
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dummy.signature"
    confirm = auth.verify_access_token(token)
    
    # Should return None because it's invalid
    assert confirm is None


@pytest.mark.anyio
async def test_verify_api_key_valid(anyio_backend):
    '''Testing the MCP auth because why not'''
    db = AsyncMock()
    
    # Mocking db query to return a fake APITable object
    mock_api_entry = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_api_entry
    db.execute.return_value = mock_result
    
    # verify_api_key lives in helfun, not auth
    # Key must have a dot (username.api_key format)
    with patch.object(auth, "hash_api_key", return_value="fake_hash"):
        result = await helfun.verify_api_key("testuser.valid_key_123", db)
    
    assert result is True
    db.execute.assert_called_once()


@pytest.mark.anyio
async def test_verify_api_key_invalid(anyio_backend):
    db = AsyncMock()
    
    # Mocking db query to return None (meaning key not found)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result
    
    # verify_api_key returns False for invalid keys, doesn't raise HTTPException
    with patch.object(auth, "hash_api_key", return_value="fake_hash"):
        result = await helfun.verify_api_key("testuser.some_random_wrong_key", db)
    
    assert result is False

# Done with this auth testing, no noticeable bugs here
