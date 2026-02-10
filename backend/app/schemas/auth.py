from pydantic import BaseModel, EmailStr, field_validator
import re

USERNAME_REGEX = re.compile(r"^[a-z][a-z0-9_]{2,29}$")
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).+$")

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str):
        v = v.lower().strip()

        if not USERNAME_REGEX.match(v):
            raise ValueError(
                "Username must be 3–30 chars, start with a letter, "
                "and contain only lowercase letters, numbers, or underscores"
            )
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if len(v) > 128:
            raise ValueError("Password is too long")

        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "Password must contain at least one letter and one number"
            )

        if v.strip() != v:
            raise ValueError("Password must not start or end with spaces")

        return v


