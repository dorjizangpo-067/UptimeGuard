import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, model_validator

# for IDE TYPE_CHECKING
if TYPE_CHECKING:
    from src.schemas.schema_url import DisplayUrl


class User(BaseModel):
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class CreateUser(User):
    password: SecretStr
    confirm_password: SecretStr
    full_name: str

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def verify_password_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class LoginUser(User):
    password: SecretStr
    model_config = ConfigDict(extra="forbid")


class PublicUserResponse(User):
    uid: uuid.UUID
    full_name: str


class PriviteUserResponse(User):
    uid: uuid.UUID
    full_name: str


class UpdateUser(BaseModel):
    full_name: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    password: SecretStr | None = Field(default=None)

    model_config = ConfigDict(extra="forbid")


class UserWithUrlsResponse(BaseModel):
    """User Profile with all their URLs"""

    uid: uuid.UUID
    email: str
    full_name: str
    is_verified: bool
    is_active: bool
    created_at: datetime
    urls: list["DisplayUrl"]

    model_config = ConfigDict(from_attributes=True)


from src.schemas.schema_url import DisplayUrl

DisplayUrl.model_rebuild()
