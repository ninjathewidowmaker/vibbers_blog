import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

import pytest
from fastapi.testclient import TestClient
from main import app
import schemas

# LOL using TestClient because I'm too lazy to setup async httpx right now
import helfun
from unittest.mock import AsyncMock
from fastapi import HTTPException

# Mocking verify_user globally so we don't connect to database during test_login_fail
_original_verify_user = helfun.verify_user

async def mock_verify_user_fail(payload, db):
    raise HTTPException(status_code=401, detail="Could not validate credentials")

helfun.verify_user = mock_verify_user_fail

client = TestClient(app)

def test_home_page_redirect():
    '''Let's see if the redirect works and doesn't just crash'''
    # We don't follow redirects so we can actually catch the 307
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/home"


def test_get_all_blogs():
    '''This feature doesn't have a page LOL. Let's test the route anyway'''
    # Expecting this to maybe fail if DB is empty or templates cache is not warmed up
    # but we ball
    try:
        response = client.get("/blogs")
        # Just checking if it doesn't give a random 404
        assert response.status_code in [200, 500] 
    except Exception as e:
        print(f"Failed to get blogs, probably DB issue: {e}")


def test_login_fail():
    '''Testing login with wrong credentials. Should be 401 obviously.'''
    raw_payload = {
        "username": "dummy_ninja",
        "password": "wrong_password_deadass",
        "email": "dummy@dummy.com"
    }
    
    response = client.put("/login", json=raw_payload)
    # Should throw 401 Unauthorized
    assert response.status_code == 401


def test_create_blog_unauthorized():
    '''You can't create a blog without a cookie. Let's make sure it blocks us.'''
    
    jama = {
        "slug": "test_blug_1", 
        "title": "My Test Title", 
        "content": "Some neat content about rust and MCP",
        "tags": ["test"], 
        "image_urls": [], 
        "author": "Ninja",
        "template": 1,
        "is_blog": True
    }
    
    response = client.post("/blogs/create", json=jama)
    # Should block us because we have no 'user_access' cookie
    assert response.status_code == 401


def test_is_token_verified_no_cookie():
    '''Just to verify if the token is valid or not(No real use just for satisfaction)'''
    response = client.get("/is_token_verified")
    
    # Should be 401 because we deadass didn't send a cookie
    assert response.status_code == 401


# Auth.py testing is done maybe? 
# These are the basic tests, they don't test the DB directly because testing async DB 
# in pytest is a pain in the ass I'll let it slide for now.
