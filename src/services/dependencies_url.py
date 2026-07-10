import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import sessionmanager
from src.errors import InvalidCredentials, InvalidToken, UrlNotFound
from src.models.model_url import URL
from src.services.service_url import Url
from src.utils.dependencies import AccessTokenBearer

AccessTokenDep = Annotated[dict, Depends(AccessTokenBearer())]
SessionDep = Annotated[AsyncSession, Depends(sessionmanager.get_session)]


def get_user_id(token_detail: AccessTokenDep) -> uuid.UUID:
    """Extract and validate user_id from token"""
    try:
        return uuid.UUID(token_detail.get("user", {}).get("user_uid"))
    except KeyError, TypeError, ValueError:
        raise InvalidToken()


async def get_url_or_404(
    uid: uuid.UUID,
    session: SessionDep,
) -> URL:
    """Get URL or raise 404"""
    url_service = Url()
    url = await url_service.get_url_by_uid(uid=uid, session=session)
    if url is None:
        raise UrlNotFound()
    return url


async def get_authorized_url(
    uid: uuid.UUID,
    session: SessionDep,
    token_detail: AccessTokenDep,
) -> URL:
    """Get URL and verify ownership"""
    user_uid = get_user_id(token_detail)
    url = await get_url_or_404(uid=uid, session=session)

    if url.user_uid != user_uid:
        raise InvalidCredentials()
    return url
