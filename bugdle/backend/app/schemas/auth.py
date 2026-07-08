from pydantic import BaseModel, field_validator


class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        # Enforced server-side regardless of any frontend check.
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v


# Login is by EMAIL (documented decision). The brief allowed email OR username;
# email is chosen to keep the lookup unambiguous and the rate-limit key stable.
class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
