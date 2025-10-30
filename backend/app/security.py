import json
import os
import time
from typing import Dict

import jwt
import requests
from cachetools import TTLCache
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# --- Cognito Configuration ---
COGNITO_REGION = os.environ.get("COGNITO_REGION", "us-east-1")
COGNITO_USER_POOL_ID = os.environ.get(
    "COGNITO_USER_POOL_ID", "us-east-1_example")
COGNITO_AUDIENCE = os.environ.get("COGNITO_AUDIENCE", "your_app_client_id")
# ---

COGNITO_ISSUER = (
    f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
)
JWKS_URL = f"{COGNITO_ISSUER}/.well-known/jwks.json"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Cache for the JWKS, expires after 1 hour
jwks_cache = TTLCache(maxsize=1, ttl=3600)


def get_jwks() -> Dict:
    """
    Fetches the JSON Web Key Set (JWKS) from Cognito.
    Caches the result to avoid repeated HTTP requests.
    """
    if "jwks" in jwks_cache:
        return jwks_cache["jwks"]

    response = requests.get(JWKS_URL)
    response.raise_for_status()
    jwks = response.json()
    jwks_cache["jwks"] = jwks
    return jwks


def get_public_key(kid: str) -> str:
    """
    Finds the public key in the JWKS corresponding to the given Key ID (kid).
    """
    jwks = get_jwks()
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Public key not found in JWKS",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    A FastAPI dependency that verifies a JWT from the request header against
    the Cognito User Pool and returns the decoded claims.
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header["kid"]

        public_key = get_public_key(kid)

        decoded_token = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=COGNITO_AUDIENCE,
            issuer=COGNITO_ISSUER,
        )

        # Verify token expiration
        if decoded_token["exp"] < time.time():
            raise jwt.ExpiredSignatureError

        return decoded_token

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while validating the token: {e}",
        )
