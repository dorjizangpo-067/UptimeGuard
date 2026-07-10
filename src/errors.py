from typing import Any, Callable

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse


class UptimeGuard(Exception):
    """This is the base class for all UprimeGuard errors"""

    pass


class InvalidToken(UptimeGuard):
    """User has provided an invalid or expired token"""

    pass


class RevokedToken(UptimeGuard):
    """User has provided a token that has been revoked"""

    pass


class AccessTokenRequired(UptimeGuard):
    """User has provided a refresh token when an access token is needed"""

    pass


class RefreshTokenRequired(UptimeGuard):
    """User has provided an access token when a refresh token is needed"""

    pass


class UserAlreadyExists(UptimeGuard):
    """User has provided an email for a user who exists during sign up."""

    pass


class InvalidCredentials(UptimeGuard):
    """User has provided wrong email or password during log in."""

    pass


class InsufficientPermission(UptimeGuard):
    """User does not have the necessary permissions to perform an action."""

    pass


class UrlNotFound(UptimeGuard):
    """URL Not found"""

    pass


class UserNotFound(UptimeGuard):
    """User Not found"""

    pass


class NothingToUpdate(UptimeGuard):
    """User Not found"""

    pass


class VerificationFailed(UptimeGuard):
    """User Not found"""

    pass


def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:

    async def exception_handler(request: Request, exc: UptimeGuard):

        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler  # type: ignore


def register_error_handlers(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "error_code": "user_not_found",
            },
        ),
    )
    app.add_exception_handler(
        UrlNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "URL not found",
                "error_code": "url_not_found",
            },
        ),
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid Email Or Password",
                "error_code": "invalid_email_or_password",
            },
        ),
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid Or expired",
                "resolution": "Please get new token",
                "error_code": "invalid_token",
            },
        ),
    )
    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or has been revoked",
                "resolution": "Please get new token",
                "error_code": "token_revoked",
            },
        ),
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid access token",
                "resolution": "Please get an access token",
                "error_code": "access_token_required",
            },
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Please provide a valid refresh token",
                "resolution": "Please get an refresh token",
                "error_code": "refresh_token_required",
            },
        ),
    )
    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "You do not have enough permissions to perform this action",
                "error_code": "insufficient_permissions",
            },
        ),
    )

    app.add_exception_handler(
        NothingToUpdate,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Nothing to Update",
                "error_code": "nothing_to_update",
            },
        ),
    )

    app.add_exception_handler(
        VerificationFailed,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Token is Invalid",
                "error_code": "failed_to_verify",
            },
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exc):

        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
