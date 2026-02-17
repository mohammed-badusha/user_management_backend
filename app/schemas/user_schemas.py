from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, date
from typing import List, Optional



ALLOWED_COUNTRY_CODES = {91, 1, 44, 971, 966, 61, 65}


def validate_phone(phone: str) -> str:
    """
    Rules:
    - Must start with + (E.164 style)
    - After + only digits
    - Total digits (without +) should be 7 to 15
    - Country code must be in ALLOWED_COUNTRY_CODES
    """
    v = phone.strip()

    if not v.startswith("+"):
        raise ValueError("Phone must start with country code like +91XXXXXXXXXX")

    digits = v[1:]
    if not digits.isdigit():
        raise ValueError("Phone must contain only digits after +")

    if len(digits) < 7 or len(digits) > 15:
        raise ValueError("Phone must have 7 to 15 digits (excluding +)")

    cc = None
    for n in (1, 2, 3):
        if len(digits) >= n:
            maybe = int(digits[:n])
            if maybe in ALLOWED_COUNTRY_CODES:
                cc = maybe
                break

    if cc is None:
        raise ValueError("Invalid/unsupported country code")

    return v  


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    is_active: bool = True

    @field_validator("first_name", "last_name")
    @classmethod
    def not_empty(cls, v: str):
        if not v.strip():
            raise ValueError("cannot be empty")
        return v

    @field_validator("phone_number")
    @classmethod
    def phone_valid(cls, v: Optional[str]):
        if v is None or v.strip() == "":
            return None
        return validate_phone(v)


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    is_active: Optional[bool] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def not_empty_if_present(cls, v: Optional[str]):
        if v is None:
            return v
        if not v.strip():
            raise ValueError("cannot be empty")
        return v

    @field_validator("phone_number")
    @classmethod
    def phone_valid(cls, v: Optional[str]):
        if v is None or v.strip() == "":
            return None
        return validate_phone(v)


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaginatedUsers(BaseModel):
    total_count: int
    page: int
    page_size: int
    data: List[UserResponse]
