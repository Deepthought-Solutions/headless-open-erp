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


from infrastructure.database import get_db
from application.rbac_service import RbacService
from sqlalchemy.orm import Session
from fastapi import Request

def get_rbac_service(db: Session = Depends(get_db)) -> RbacService:
    return RbacService(db)

class PermissionChecker:
    def __init__(self, permission: str, resource_name: str = None):
        self.permission = permission
        self.resource_name = resource_name

    async def __call__(
        self,
        request: Request,
        user: TokenData = Depends(get_current_user),
        rbac_service: RbacService = Depends(get_rbac_service)
    ):
        # Determine if this is a resource-specific or global permission check
        if self.resource_name:
            resource_name_to_check = self.resource_name
            resource_id_key = f"{self.resource_name}_id"
            if resource_id_key not in request.path_params:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Configuration error: Resource ID key '{resource_id_key}' not found in request path."
                )
            resource_id_to_check = int(request.path_params[resource_id_key])
        else:
            # Convention for global permissions (resource_name is None)
            resource_name_to_check = "global"
            resource_id_to_check = 0

        has_permission = rbac_service.check_user_permission_for_resource(
            user_sub=user.username,
            permission_name=self.permission,
            resource_name=resource_name_to_check,
            resource_id=resource_id_to_check
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action."
            )
