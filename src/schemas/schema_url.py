import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.schemas.schema_auth import PublicUserResponse


class URL(BaseModel):
    """Url Base Schema"""

    url: str

    model_config = ConfigDict(from_attributes=True)


class CreateUrl(URL):
    """Creating Url Schema"""

    pass


class UserUrlResponse(URL):
    """Display both URL and User"""

    uid: uuid.UUID
    user_uid: uuid.UUID
    created_at: datetime
    user: PublicUserResponse
