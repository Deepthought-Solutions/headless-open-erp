import httpx
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
import os
# The OIDC provider's URL within the Docker network
OIDC_PROVIDER_URL = os.environ.get('OCTOBRE_ISSUER_URL', "http://localhost:3080")
WELL_KNOWN_ENDPOINT = "/.well-known/openid-configuration"

# This is used by FastAPI to extract the token from the Authorization header.
# The tokenUrl is not actually used in this OIDC flow, but it's a required parameter.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=OIDC_PROVIDER_URL + "/token")

logger = logging.getLogger(__name__)

class TokenData(BaseModel):
    username: str | None = None

async def get_oidc_config():
    """Fetches OIDC provider configuration."""
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{OIDC_PROVIDER_URL}{WELL_KNOWN_ENDPOINT}")
            res.raise_for_status()
            return res.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as exc:
            logger.exception("Error contacting OIDC provider")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error contacting OIDC provider: {exc}",
            )

async def get_jwks(oidc_config: dict):
    """Fetches JSON Web Key Set (JWKS) from the OIDC provider."""
    jwks_uri = oidc_config.get("jwks_uri")
    if not jwks_uri:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="jwks_uri not found in OIDC configuration",
        )
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(jwks_uri)
            res.raise_for_status()
            return res.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as exc:
            logger.exception("OIDC provider's JWKS URI returned an error")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"OIDC provider's JWKS URI returned an error: {exc}",
            )


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    FastAPI dependency to verify the OIDC token and return the user's claims.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        oidc_config = await get_oidc_config()
        jwks = await get_jwks(oidc_config)

        issuer = oidc_config.get("issuer")
        if not issuer:
            raise credentials_exception

        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            # In a real-world app, we should validate the audience.
            options={"verify_aud": False},
            issuer=issuer,
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        logger.exception("Could not validate credentials")
        raise credentials_exception
    return token_data
