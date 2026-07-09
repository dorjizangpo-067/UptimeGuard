import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

# for IDE TYPE_CHECKING purpose
if TYPE_CHECKING:
    from src.schemas.schema_auth import PublicUserResponse


class URL(BaseModel):
    """Url Base Schema"""

    url: str

    model_config = ConfigDict(from_attributes=True)


class CreateUrl(URL):
    """Creating Url Schema"""

    pass


class DisplayUrl(URL):
    """Display url"""

    uid: uuid.UUID
    url: str
    created_at: datetime
    user_uid: uuid.UUID


class UpdateUrl(URL):
    """Update Url"""

    pass


class UserUrlResponse(URL):
    """Display both URL and User"""

    uid: uuid.UUID
    user_uid: uuid.UUID
    created_at: datetime
    user: "PublicUserResponse"


from src.schemas.schema_auth import PublicUserResponse

PublicUserResponse.model_rebuild()
