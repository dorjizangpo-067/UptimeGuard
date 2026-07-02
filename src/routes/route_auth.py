from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import sessionmanager
from src.schemas.schema_auth import CreateUser, PriviteUserResponse
from src.services.service_auth import Auth

auth_router = APIRouter()

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
