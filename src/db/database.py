import ssl
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.config import config


class SessionManager:
    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None

    def init_db(self) -> None:
        """Initialize the async engine and session factory with connection pooling."""

        database_url = config.DATABASE_URL.get_secret_value()

        # Ensure asyncpg driver and strip query parameters for SSL compatibility
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace(
                "postgresql://", "postgresql+asyncpg://"
            )
        database_url = (
            database_url.split("?")[0] if "?" in database_url else database_url
        )

        # 2. Create SSL context for secure cloud DB connections
        ssl_context = ssl.create_default_context()

        # Engine Setup
        self.engine = create_async_engine(
            database_url,
            pool_size=config.POOL_SIZE,
            max_overflow=config.MAX_OVERFLOW,
            pool_pre_ping=True,
            connect_args={"ssl": ssl_context},
            echo=True,  # TODO: for development only
        )

        # session factory setup
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False,
            class_=AsyncSession,
        )

    async def close(self) -> None:
        """Cleanly close all pool connections on app shutdown."""
        if self.engine:
            await self.engine.dispose()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Yield an ORM session. Automatically rolls back if an operation crashes."""
        if not self.session_factory:
            raise RuntimeError("Database session factory is not initialized.")

        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise


sessionmanager = SessionManager()


class Base(DeclarativeBase):
    pass
