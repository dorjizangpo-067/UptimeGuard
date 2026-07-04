from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.requests import Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.schema_auth import PriviteUserResponse
from src.services.service_auth import Auth
from src.utils.jwt_setup import decode_token

user_services = Auth()


class TokenBearer(HTTPBearer):
    """Base FastAPI dependency for validating JWT Bearer tokens.

    Subclasses must override `verify_token_data` to enforce rules specific
    to the token type they accept (e.g. access vs refresh). Use as
    `Depends(AccessTokenBearer())` or `Depends(RefreshTokenBearer())`.
    """

    def __init__(self, auto_error: bool = True) -> None:
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict[str, Any] | None:  # type: ignore[override]
        """Extract, decode, and validate the Bearer token on `request`.

        Returns:
            The decoded token payload (claims dict).

        Raises:
            HTTPException: 403 if the header is missing, the token can't
                be decoded, or it fails subclass-specific validation.
        """

        # Only reachable when auto_error=False and no header was sent;
        # with auto_error=True HTTPBearer raises before we get here.
        creds = await super().__call__(request)
        if creds is None:
            return None

        token = creds.credentials
        token_data = decode_token(token=token)

        # decode_token returns None then Exception raise
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or expired",
                    "resolution": "Please get new token",
                },
            )

        # chiled class to ckeck token is access or refresh token
        self.verify_token_data(token_data=token_data)

        return token_data

    def verify_token_data(self, token_data: dict[str, Any]) -> None:
        """Enforce token-type-specific rules. Must be overridden.

        Raises:
            HTTPException: if `token_data` fails the subclass's rule.
        """

        raise NotImplementedError("Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    """Dependency for routes that require an access token."""

    def verify_token_data(self, token_data: dict) -> None:
        # reject refresh token
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token",
            )


class RefreshTokenBearer(TokenBearer):
    """Dependency for routes that require a refresh token (e.g. /auth/refresh)."""

    def verify_token_data(self, token_data: dict) -> None:
        # reject access token
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a refresh token",
            )


def is_token_valid(token: str) -> bool:
    """Verify token validity
    Args:
        token: str

    Returns:
        True if valid and False if Invalid token
    """
    token_data = decode_token(token=token)
    if token_data is None:
        return False
    return True


async def get_current_user(
    token_data: Annotated[dict, Depends(AccessTokenBearer())], session: AsyncSession
) -> PriviteUserResponse | None:
    """Get Current User (extract from token_data and search from Database)
    Args:
        token_data: dict[str, Any]

    Returns:
        user Data or None if email in token_data is invilad
    """

    user_emil = token_data["user"]["email"]
    user = await user_services.get_user_by_email(email=user_emil, session=session)
    if user is None:
        return None
    return PriviteUserResponse.model_validate(user)
