from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    # EmailStr enforces format server-side; never trust the client's
    # type="email" check as the only guard (the JS may not run at all).
    email: EmailStr
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
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
