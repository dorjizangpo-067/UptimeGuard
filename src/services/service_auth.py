from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.model_auth import User
from src.schemas.schema_auth import CreateUser, PriviteUserResponse
from src.utils.utils import generate_password_hash


class Auth:
    # fetching user by email
    async def get_user_by_email(
        self, email: EmailStr, session: AsyncSession
    ) -> User | None:
        statement = select(User).where(User.email == email)
        result = await session.execute(statement=statement)

        return result.scalar_one_or_none()

    # check user exist or not
    async def user_exist(self, email: EmailStr, session: AsyncSession) -> bool:
        user = await self.get_user_by_email(email=email, session=session)
        if user is None:
            return False
        return True

    # creating new user
    async def user_create(
        self, user_data: CreateUser, session: AsyncSession
    ) -> PriviteUserResponse:
        password_hashed = generate_password_hash(
            password=user_data.password.get_secret_value()
        )
        new_user = User(
            username=user_data.username,
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
        for k, v in update_user.items():
            setattr(user, k, v)
        session.add(user)
        await session.commit()
        await session.refresh(user)

        return PriviteUserResponse.model_validate(user)
