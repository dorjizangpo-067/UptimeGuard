import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.model_url import URL
from src.schemas.schema_url import CreateUrl, DisplayUrl, UpdateUrl, UserUrlResponse
from src.utils.dependencies import AccessTokenBearer

AccessTokenDep = Annotated[dict, Depends(AccessTokenBearer())]


class Url:
    """Url Service"""

    async def get_url_by_uid(self, uid: uuid.UUID, session: AsyncSession) -> URL | None:
        """Get URL
        Args:
            uid: uuid.UUID
            session: AsyncSession
        Returns:
            url or None if dont exist
        """

        statement = select(URL).where(URL.uid == uid)
        result = await session.execute(statement=statement)
        return result.scalar_one_or_none()

    async def create_url(
        self, user_uid: uuid.UUID, url_data: CreateUrl, session: AsyncSession
    ) -> DisplayUrl:
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

        return DisplayUrl.model_validate(new_url)

    async def update_url(
        self, url: URL, update_url: UpdateUrl, session: AsyncSession
    ) -> DisplayUrl:
        """Update Url
        Args:
            url: URL
            update_url: dict
            session: AsyncSession
        Returns:
            updated url
        """

        update_data = update_url.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(url, k, v)

        await session.commit()
        await session.refresh(url)
        return DisplayUrl.model_validate(url)

    async def delete_url(self, url_to_delete: URL, session: AsyncSession) -> None:
        """Delet Url
        Args:
            url_to_delete: URL
            session: AsyncSession
        Returns:
            None
        """

        await session.delete(url_to_delete)
        await session.commit()
