import os
from typing import Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from backend.app.firebase_config import firebase_auth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(id_token: str = Depends(oauth2_scheme)) -> Dict:
    """
    A FastAPI dependency that verifies a Firebase ID token from the request header
    and returns the decoded claims.
    """
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

