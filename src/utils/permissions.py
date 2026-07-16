from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import sessionmanager
from src.errors import InvalidToken, NotVerified, UserNotFound
from src.services.service_auth import Auth
from src.utils.dependencies import AccessTokenBearer

SessionDep = Annotated[AsyncSession, Depends(sessionmanager.get_session)]
AccessTokenDep = Annotated[dict, Depends(AccessTokenBearer())]
user_services = Auth()


# Verified User Check
async def verified_user_dependency(
    token_detail: AccessTokenDep,
    session: SessionDep,
):
    """Check if user is verified"""
    user = await user_services.get_current_user(
        token_data=token_detail, session=session
    )

    if not user:
        raise UserNotFound()

    if not user.is_verified:
        raise NotVerified()

    return user


# Role-based Check (example)
# async def admin_user_dependency(
#     token_detail: AccessTokenDep,
#     session: SessionDep,
# ):
#     """Check if user is admin"""
#     user = await user_services.get_current_user(
#         token_data=token_detail, session=session
#     )
#
#     if not user:
#         raise UserNotFound()
#
#     if user.role != "admin":  # Adjust based on your User model
#         raise InvalidToken("Admin access required")
#
#     return user


# Annotated types for easy import
# AdminUserDep = Annotated[dict, Depends(admin_user_dependency)]
