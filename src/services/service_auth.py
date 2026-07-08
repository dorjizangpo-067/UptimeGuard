from typing import Any

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.model_auth import User
from src.schemas.schema_auth import CreateUser, PriviteUserResponse
from src.utils.utils import generate_password_hash


class Auth:
    """Auth Services"""

    async def get_user_by_email(
        self, email: EmailStr, session: AsyncSession
    ) -> User | None:
        """Fetch user with email
        Args:
            email: EmailStr
            session: AsyncSession
        Returns:
            user with matching email or None
        """

        statement = select(User).where(User.email == email)
        result = await session.execute(statement=statement)

        return result.scalar_one_or_none()

    async def email_exist(self, email: EmailStr, session: AsyncSession) -> bool:
        """Check User email already exist in Database
        Args:
            email: EmailStr
            session: AsyncSession
        Returns:
            True or False
        """

        user_by_email = await self.get_user_by_email(email=email, session=session)
        if user_by_email is None:
            return False
        return True

    async def get_current_user(
        self,
        token_data: dict[str, Any],
        session: AsyncSession,
    ) -> User | None:
        """Get Current User (extract from token_data and search from Database)
        Args:
            token_data: dict[str, Any]

        Returns:
            user Data or None if email in token_data is invilad
        """

        user_emil = token_data["user"]["email"]
        user = await self.get_user_by_email(email=user_emil, session=session)
        if user is None:
            return None
        return user

    async def user_create(
        self, user_data: CreateUser, session: AsyncSession
    ) -> PriviteUserResponse:
        """Create New User
        Args:
            user_data: CreateUser
            session: AsyncSession
        Returns:
            new User
        """

        # hash provided Password
        password_hashed = generate_password_hash(
            password=user_data.password.get_secret_value()
        )

        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            password_hashed=password_hashed,
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return PriviteUserResponse.model_validate(new_user)

    async def update_user(
        self, user: User, update_user: dict, session: AsyncSession
    ) -> PriviteUserResponse:
        """Update User Data
        Args:
            user: User
            update_user: dict
            session: AsyncSession
        Returns:
            Updated User
        """

        for k, v in update_user.items():
            setattr(user, k, v)

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return PriviteUserResponse.model_validate(user)
