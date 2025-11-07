from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username или email")
    password: str = Field(..., min_length=1, description="Пароль")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str

