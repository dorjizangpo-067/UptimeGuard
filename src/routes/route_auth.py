from datetime import timedelta
from tokenize import Token
from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_mail import NameEmail
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import config
from src.db.database import sessionmanager
from src.db.redis import add_jti_to_blocklist
from src.errors import (
    InvalidCredentials,
    InvalidToken,
    NothingToUpdate,
    UserAlreadyExists,
    UserNotFound,
    VerificationFailed,
)
from src.mail import create_message, mail
from src.schemas.schema_auth import (
    CreateUser,
    EmailSchema,
    LoginUser,
    PriviteUserResponse,
    UpdateUser,
    UserWithUrlsResponse,
)
from src.services.service_auth import Auth
from src.utils.dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
)
from src.utils.jwt_setup import create_access_token
from src.utils.utils import (
    create_url_save_token,
    decode_url_safe_token,
    generate_password_hash,
    verify_password,
)

auth_router = APIRouter(tags=["Auth"])

user_services = Auth()

# Dependencies
SessionDep = Annotated[AsyncSession, Depends(sessionmanager.get_session)]
AccessTokenDep = Annotated[dict, Depends(AccessTokenBearer())]
RefreshTokenDep = Annotated[dict, Depends(RefreshTokenBearer())]


@auth_router.post("/send_mail")
async def send_mail(email_schema: EmailSchema) -> dict[str, str]:
    recipients = [
        NameEmail(name=r.name, email=r.email) for r in email_schema.recipients
    ]

    html = "<h1>Welcome to the app</h1>"
    subject = "Welcome to our app"

    message = await create_message(recipients=recipients, sub=subject, body=html)
    await mail.send_message(message)

    return {"message": "Email sent successfully"}


@auth_router.post("/signup")
async def create_user(user_data: CreateUser, session: SessionDep) -> dict[str, Any]:
    """User Signup
    Args:
        user_data: CreateUser
        session: SessionDep
    Returns:
        user: PriviteUserResponse > New User Data
    """

    # Check user email already exist
    email_exist = await user_services.email_exist(
        email=user_data.email, session=session
    )
    if email_exist:
        raise UserAlreadyExists()

    user = await user_services.user_create(user_data=user_data, session=session)

    token = create_url_save_token({"email": user.email})
    link = f"http://{config.DOMAIN}/api/v1/auth/verify/{token}"
    html_message = f"""
        <h1>Verify your Email</h1>
        <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """
    message = await create_message(
        recipients=[NameEmail(name=user.full_name, email=user.email)],
        sub="Verify your email",
        body=html_message,
    )
    await mail.send_message(message)

    return {
        "user": PriviteUserResponse.model_validate(user),
        "message": "Account Created! Check email to verify your account",
    }


@auth_router.post("/verify/{token}")
async def verify_token(token: str, session: SessionDep):
    """User Account Verification
    Args:
        token: str -> itsdengerous token
        session: SessionDep
    Returns:
        JSONResponse for success and Error
    Raise:
        UserNotFound, VerificationFailed
    """

    token_data = decode_url_safe_token(token=token)

    # is token Valid
    if not token_data:
        raise VerificationFailed()

    user_email = token_data.get("email")

    if user_email:
        # user with this email exist
        user = await user_services.get_user_by_email(email=user_email, session=session)

        if not user:
            raise UserNotFound()

        # update is_verified to True
        await user_services.update_user(
            user=user, update_user={"is_verified": True}, session=session
        )
        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@auth_router.patch("/{email}")
async def update_user(
    email: EmailStr,
    update_data: UpdateUser,
    session: SessionDep,
    token_detail: AccessTokenDep,
) -> PriviteUserResponse:
    """Update User Data
    Args:
        email: EmailStr
        update_data: UpdateUser
        session: SessionDep

    Returns:
        user: PriviteUserResponse > Updated User Data

    """
    current_user = await user_services.get_current_user(
        token_data=token_detail, session=session
    )

    if current_user is None:
        raise UserNotFound()

    if current_user.email != email:
        raise InvalidCredentials()

    # Prepare update dictionary, ignoring unset fields
    update_dict = update_data.model_dump(exclude_unset=True)

    # Handle password hashing if provided
    if "password" in update_dict and update_dict["password"] is not None:
        update_dict["password_hashed"] = generate_password_hash(
            password=update_dict["password"].get_secret_value()
        )
        del update_dict["password"]  # Remove plain password from dict

    # No fields to update
    if not update_dict:
        raise NothingToUpdate()

    updated_user = await user_services.update_user(
        user=current_user, update_user=update_dict, session=session
    )

    return PriviteUserResponse.model_validate(updated_user)


@auth_router.post("/login")
async def login(login_data: LoginUser, session: SessionDep) -> dict[str, Any]:
    """Login User
    Args:
        login_data: LoginUser
        session: AsyncSession
    Returns:
        message: dict > login message with tokens
    """
    user = await user_services.get_user_by_email(
        email=login_data.email, session=session
    )

    # Check if user exists and password is correct
    if not user or not verify_password(
        password=login_data.password.get_secret_value(),
        hash_password=user.password_hashed,
    ):
        raise InvalidCredentials()

    # jwt_payload data
    payload = {
        "email": user.email,
        "user_uid": str(user.uid),
    }

    # generate access and refresh token
    access_token = create_access_token(user_data=payload)
    refresh_token = create_access_token(
        user_data=payload,
        refresh=True,
        expiry=timedelta(days=config.JWT_REFRESH_TOKEN_EXPIRY),
    )

    return {
        "message": "Login Successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "email": user.email,
            "uid": str(user.uid),
        },
    }


@auth_router.get("/refresh")
async def get_new_access_token(token_detail: RefreshTokenDep) -> dict:
    """Generating new Access token Through Refresh Token
    Args:
        token_detail: RefreshTokenDep
    Returns:
        new_access_token: dict
    """

    # creating new access token
    # The RefreshTokenDep already ensures the token is not expired.
    new_access_token = create_access_token(user_data=token_detail["user"])

    return {"new_access_token": new_access_token}


@auth_router.get("/me")
async def get_current_user_route(
    token_detail: AccessTokenDep, session: SessionDep
) -> UserWithUrlsResponse | None:
    """Get Current user route
    Args:
        token_data: AccessTokenDep,
        session: SessionDep
    Returns:
        PriviteUserResponse or None
    """

    user = await user_services.get_current_user(
        token_data=token_detail, session=session
    )

    if user is None:
        raise InvalidToken()

    return UserWithUrlsResponse.model_validate(user)


@auth_router.get("/logout")
async def logout(token_detail: AccessTokenDep) -> dict:
    """Logout jti (Block the JWT id)
    Args:
        token_detail: AccessTokenDep
    Returns:
        message"""

    jti = token_detail["jti"]
    await add_jti_to_blocklist(jti=jti)
    return {"content": "Logout Out Successfully"}
