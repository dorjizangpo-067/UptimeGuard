import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
