from redis import asyncio as aioredis

from src.config import config

token_blocklist = aioredis.from_url(config.REDIS_URL)


async def add_jti_to_blocklist(jti: str) -> None:
    """Set jti value to redis after revoke
    Args:
        jti: str
    Returns:
        None
    """
    await token_blocklist.set(name=jti, value="", ex=config.JTI_EXPIRY)


async def token_in_blocklist(jti: str) -> bool:
    """Get jti value from redis
    Args:
        jti: str
    Returns:
        Bool
    """
    value = await token_blocklist.get(jti)
    return value is not None
