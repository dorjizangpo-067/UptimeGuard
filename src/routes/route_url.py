import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import sessionmanager
from src.models.model_url import URL
from src.schemas.schema_url import CreateUrl, DisplayUrl, UpdateUrl, UserUrlResponse
from src.services.dependencies_url import get_authorized_url
from src.services.service_url import Url
from src.utils.dependencies import AccessTokenBearer

url_router = APIRouter()

# Dependencies
url_services = Url()
AccessTokenDep = Annotated[dict, Depends(AccessTokenBearer())]
SessionDep = Annotated[AsyncSession, Depends(sessionmanager.get_session)]
AuthorizedUrlDep = Annotated[URL, Depends(get_authorized_url)]


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
    update_url_data: UpdateUrl, session: SessionDep, url: AuthorizedUrlDep
) -> DisplayUrl:
    """Update URL route
    Args:
        uid: uuid.UUID
        update_url_data: dict
        url: AuthorizedUrlDep
    Returns:
        update_url
    """

    update_url = await url_services.update_url(
        url=url, update_url=update_url_data, session=session
    )

    return update_url


@url_router.delete("/{uid}", status_code=status.HTTP_200_OK)
async def delete_url(session: SessionDep, url: AuthorizedUrlDep):
    """Delete URL route
    Args:
        session: SessionDep,
        url: AuthorizedUrlDep
    Returns:
        null
    """

    await url_services.delete_url(url_to_delete=url, session=session)
