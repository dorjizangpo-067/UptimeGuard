import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import sessionmanager
from src.schemas.schema_url import CreateUrl, DisplayUrl, UpdateUrl, UserUrlResponse
from src.services.service_url import Url
from src.utils.dependencies import AccessTokenBearer

url_router = APIRouter()

# Dependencies
url_services = Url()
AccessTokenDep = Annotated[dict, Depends(AccessTokenBearer())]
SessionDep = Annotated[AsyncSession, Depends(sessionmanager.get_session)]


@url_router.post("/")
async def create_url(
    url_data: CreateUrl, session: SessionDep, token_detail: AccessTokenDep
) -> UserUrlResponse:
    """Create new Url
    Args:
        url_data: CreateUrl
        session: SessionDep
        token_detail: AccessTokenDep
    Returns:
        new_url
    """
    try:
        user_uid = uuid.UUID(token_detail.get("user", {}).get("user_uid"))
    except KeyError, TypeError, ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")

    new_url = await url_services.create_url(
        user_uid=user_uid, url_data=url_data, session=session
    )
    return new_url


@url_router.put("/{uid}")
async def update_url(
    uid: uuid.UUID,
    update_url_data: UpdateUrl,
    session: SessionDep,
    token_detail: AccessTokenDep,
) -> DisplayUrl:
    """Update URL route
    Args:
        uid: uuid.UUID
        update_url_data: dict
        session: SessionDep
    Returns:
        update_url
    """

    try:
        user_uid = uuid.UUID(token_detail.get("user", {}).get("user_uid"))
    except KeyError, TypeError, ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # make sure url is found
    url = await url_services.get_url_by_uid(uid=uid, session=session)
    if url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="URL doesnot exist"
        )

    # Authorization check
    if url.user_uid != user_uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    update_url = await url_services.update_url(
        url=url, update_url=update_url_data, session=session
    )

    return update_url
