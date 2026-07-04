from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import config
from src.db.database import sessionmanager
from src.schemas.schema_auth import (
    CreateUser,
    LoginUser,
    PriviteUserResponse,
    UpdateUser,
)
from src.services.service_auth import Auth
from src.utils.jwt_setup import create_access_token
from src.utils.utils import generate_password_hash, verify_password

auth_router = APIRouter(tags=["Auth"])

user_services = Auth()

# Dependencies
SessionDep = Annotated[AsyncSession, Depends(sessionmanager.get_session)]


@auth_router.post("/signup")
async def create_user(
    user_data: CreateUser, session: SessionDep
) -> PriviteUserResponse:
    """User Signup
    Args:
        user_data: CreateUser
        session: SessionDep
    Returns:
        user: PriviteUserResponse > New User Data
    """

    # Check user email already exist
    user_exist = await user_services.user_exist(email=user_data.email, session=session)
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email aleady exist",
        )

    user = await user_services.user_create(user_data=user_data, session=session)
    return PriviteUserResponse.model_validate(user)


@auth_router.patch("/{email}")
async def update_user(
    email: EmailStr, update_data: UpdateUser, session: SessionDep
) -> PriviteUserResponse:
    """Update User Data
    Args:
        email: EmailStr
        update_data: UpdateUser
        session: SessionDep

    Returns:
        user: PriviteUserResponse > Updated User Data

    """
    # Check if user exists
    existing_user = await user_services.get_user_by_email(email=email, session=session)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    updated_user = await user_services.update_user(
        user=existing_user, update_user=update_dict, session=session
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email or Password Is incorrect",
        )

    # jwt_payload data
    payload = {
        "email": user.email,
        "user_uid": str(user.uid),
    }

    # generate access token (JWT)
    access_token = create_access_token(user_data=payload)

    # generate access token (JWT)
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
            "username": user.username,
        },
    }
