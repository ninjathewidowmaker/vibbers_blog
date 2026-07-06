import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import asyncio
load_dotenv()


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')


password_hash = PasswordHash.recommended()

def get_hash_pswd(password):
    '''return a hashed password'''
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password):
    '''give a hash and returns a bool, True or False. If True then it's valid if False then invalid'''
    return password_hash.verify(plain_password, hashed_password)

#magma = verify_password('jumbo','$argon2id$v=19$m=65536,t=3,p=4$6drGicrgzf9Dkfat7Bt/Kw$U9WtzDnQ9ul79SZ1yWzAdj2UKkAt49ZzrLY6DA8lbjc')
#print(magma)

#JWT related 
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

user_details = {
    'username' : 'niNjAtHeWiDoWmAkEr96',
    'role' : 'admin'
}

token = create_access_token(user_details, expires_delta=timedelta(minutes=60))
print(token)