from pydantic import BaseModel, Field, EmailStr, field_validator
import re


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username must be 3-20 alphanumeric characters or underscores.",
    )

    email: EmailStr

    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        pattern = (
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        )
        if not re.match(pattern, v):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one number, and one special character."
            )
        return v
