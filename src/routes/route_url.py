from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import sessionmanager
from src.models.model_url import URL
from src.schemas.schema_url import CreateUrl, DisplayUrl, UpdateUrl
from src.services.dependencies_url import get_authorized_url
from src.services.service_auth import Auth
from src.services.service_url import Url
from src.utils.dependencies import AccessTokenBearer

url_router = APIRouter()

# Dependencies
url_services = Url()
auth_services = Auth()
AccessTokenDep = Annotated[dict, Depends(AccessTokenBearer())]
SessionDep = Annotated[AsyncSession, Depends(sessionmanager.get_session)]
AuthorizedUrlDep = Annotated[URL, Depends(get_authorized_url)]


@url_router.post("/")
async def create_url(
    url_data: CreateUrl, session: SessionDep, token_detail: AccessTokenDep
) -> DisplayUrl:
    """Create new Url
    Args:
        url_data: CreateUrl
        session: SessionDep
        token_detail: AccessTokenDep
    Returns:
        new_url
    """

    user = await auth_services.get_current_user(
        token_data=token_detail, session=session
    )
    user_uid = user.uid

    new_url = await url_services.create_url(
        user_uid=user_uid, url_data=url_data, session=session
    )
    return DisplayUrl.model_validate(new_url)


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
