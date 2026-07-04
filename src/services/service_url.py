import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.model_url import URL
from src.schemas.schema_url import CreateUrl, UserUrlResponse
from src.utils.dependencies import AccessTokenBearer

AccessTokenDep = Annotated[dict, Depends(AccessTokenBearer())]


class Url:
    """Url Service"""

    async def create_url(
        self, user_uid: uuid.UUID, url_data: CreateUrl, session: AsyncSession
    ) -> UserUrlResponse:
        """Creating new url
        Args:
            user_uid: uuid.UUID
            url_data: CreateUrl
            session: AsyncSession
        Returns:
            UserUrlResponse
        """

        url_data_dict = url_data.model_dump()
        new_url = URL(**url_data_dict)

        new_url.user_uid = user_uid

        session.add(new_url)
        await session.commit()
        await session.refresh(new_url)

        return UserUrlResponse.model_validate(new_url)
