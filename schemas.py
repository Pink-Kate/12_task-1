from pydantic import BaseModel, EmailStr, validator
from datetime import date, datetime
from typing import Optional

# Authentication schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Пароль повинен містити мінімум 6 символів')
        return v

class User(UserBase):
    id: int
    is_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    token_type: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class EmailVerification(BaseModel):
    token: str

class UserAvatarUpdate(BaseModel):
    avatar_url: str

# Contact schemas
class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birth_date: date
    additional_data: Optional[str] = None

    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v or not v.strip():
            raise ValueError('Ім\'я та прізвище не можуть бути порожніми')
        return v.strip()

    @validator('phone')
    def validate_phone(cls, v):
        if not v or not v.strip():
            raise ValueError('Номер телефону не може бути порожнім')
        return v.strip()

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    additional_data: Optional[str] = None

    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Ім\'я та прізвище не можуть бути порожніми')
        return v.strip() if v else v

    @validator('phone')
    def validate_phone(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Номер телефону не може бути порожнім')
        return v.strip() if v else v

class Contact(ContactBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True