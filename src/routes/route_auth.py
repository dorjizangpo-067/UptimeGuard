from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import sessionmanager
from src.schemas.schema_auth import CreateUser, PriviteUserResponse, UpdateUser
from src.services.service_auth import Auth
from src.utils import generate_password_hash  # Import for hashing new password

auth_router = APIRouter(tags=["Auth"])

user_services = Auth()

# Dependies
SessionDep = Annotated[AsyncSession, Depends(sessionmanager.get_session)]


@auth_router.post("/signup")
async def create_user(
    user_data: CreateUser, session: SessionDep
) -> PriviteUserResponse:
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

    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    updated_user = await user_services.update_user(
        user=existing_user, update_user=update_dict, session=session
    )
    return PriviteUserResponse.model_validate(updated_user)
