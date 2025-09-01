from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: str
    name: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class MFAVerify(BaseModel):
    code: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    mfa_enabled: bool
    created_at: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class MFASetup(BaseModel):
    secret: str
    qr_code: str
