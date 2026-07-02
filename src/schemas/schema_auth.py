from pydantic import BaseModel, EmailStr, Field, SecretStr, model_validator


class User(BaseModel):
    email: EmailStr


class CreateUser(User):
    password: SecretStr
    confirm_password: SecretStr
    username: str = Field(max_length=30)
    full_name: str

    @model_validator(mode="after")
    def verify_password_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class LoginUser(User):
    password: SecretStr


class PriviteUser(User):
    password: SecretStr
    username: str = Field(max_length=30)
    full_name: str
