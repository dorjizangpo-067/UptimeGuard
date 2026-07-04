import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import sessionmanager
from src.schemas.schema_url import CreateUrl, UserUrlResponse
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
    user_uid = uuid.UUID(token_detail.get("user", {}).get("user_uid"))
    new_url = await url_services.create_url(
        user_uid=user_uid, url_data=url_data, session=session
    )
    return new_url
