import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

import pytest
from unittest.mock import AsyncMock, MagicMock
import helfun
import schemas
import models
import auth
from fastapi import HTTPException

# Since we don't have pytest-asyncio installed, we use anyio which is already
# configured in your project. We just need to define this fixture:
@pytest.fixture
def anyio_backend():
    return 'asyncio'

# To run async tests, we mark them with pytest.mark.anyio
# Since helfun has all the core logic, testing it here makes total sense because
# both main.py and mcp_main.py use these functions!

@pytest.mark.anyio
async def test_create_new_blog_helfun(anyio_backend):
    '''Test if creating a blog adds it to DB and commits'''
    db = AsyncMock()
    
    # Mocking refresh to fake database autoincrement ID
    async def fake_refresh(obj):
        obj.id = 1337
    db.refresh.side_effect = fake_refresh
    
    payload = schemas.BlogCreate(
        slug="neat-rust-article",
        title="Why Rust is awesome",
        content="Rust is cool and memory safe...",
        tags=["rust", "coding"],
        image_urls=[],
        author="ninja",
        template=1
    )
    
    result = await helfun.create_new_blog(payload, db)
    
    assert result["message"] == "Your Blog post created a successfully"
    assert result["blog_id"] == 1337
    db.add.assert_called_once()
    db.commit.assert_called_once()


@pytest.mark.anyio
async def test_del_blog_helfun(anyio_backend):
    '''Make sure delete executes the delete statement and commits'''
    db = AsyncMock()
    
    result = await helfun.del_blog("old-slug-to-delete", db)
    
    assert "deleted successufully" in result
    assert "old-slug-to-delete" in result
    db.execute.assert_called_once()
    db.commit.assert_called_once()


@pytest.mark.anyio
async def test_edit_blogs_not_found(anyio_backend):
    '''If blog doesn't exist, we should get a 404 HTTPException'''
    db = AsyncMock()
    
    # Mock execute returning no blog scalar
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result
    
    payload = schemas.BlogUpdate(title="New Title")

    # edit_blogs raises HTTPException(404) when blog not found
    with pytest.raises(HTTPException) as excinfo:
        await helfun.edit_blogs("fake-slug", payload, db)
    assert excinfo.value.status_code == 404


@pytest.mark.anyio
async def test_create_user_helfun(anyio_backend):
    '''Test user creation, hashing password, and saving to DB'''
    db = AsyncMock()
    
    async def fake_refresh(obj):
        obj.id = 42
    db.refresh.side_effect = fake_refresh
    
    # Field is named hashed_password in the schema (it accepts plaintext, gets hashed server-side)
    payload = schemas.CreateUser(
        username="new_ninja",
        hashed_password="plain_text_password",
        email="ninja@vibbers.com"
    )
    
    result = await helfun.create_user(payload, db)
    
    assert "successfully created with id 42" in result
    db.add.assert_called_once()
    db.commit.assert_called_once()
    
    # Check that it saved the hashed password, not the plain text one!
    saved_user = db.add.call_args[0][0]
    assert saved_user.username == "new_ninja"
    assert saved_user.hashed_password != "plain_text_password"
    assert auth.verify_password("plain_text_password", saved_user.hashed_password) is True


@pytest.mark.anyio
async def test_verify_user_wrong_password(anyio_backend):
    '''Let's see if verifying with a bad password throws a 401 exception'''
    db = AsyncMock()
    
    # Mocking DB response to return a valid password hash for 'admin'
    real_hash = auth.get_hash_pswd("correctpassword")
    mock_result = MagicMock()
    mock_result.scalar.return_value = real_hash
    db.execute.return_value = mock_result
    
    payload = schemas.VerifyUser(
        username="admin",
        password="wrong_password"
    )
    
    with pytest.raises(HTTPException) as excinfo:
        await helfun.verify_user(payload, db)
    
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could not validate credentials"
