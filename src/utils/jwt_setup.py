import logging
import uuid
from datetime import timedelta
from typing import Any

import jwt

from src.config import config


def create_access_token(
    user_data: dict[str, Any],
    expiry: timedelta | None = None,
    refresh: bool | None = None,
) -> str:
    if expiry is None:
        expiry = timedelta(seconds=config.JWT_EXPIRY)

    payload = {
        "user": user_data,
        "exp": expiry,
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }
    token = jwt.encode(
        payload=payload,
        key=config.JWT_SECRET_KEY.get_secret_value(),
        algorithm=config.JWT_ALGORITHM,
    )
    return token


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=config.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[config.JWT_ALGORITHM],
        )
        return token_data
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None
