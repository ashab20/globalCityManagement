from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class ShopRenterProfileBase(BaseModel):
    renter_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    nid_number: Optional[str] = None
    created_by: Optional[int] = None
    update_by: Optional[int] = None
    active_status: Optional[int] = 1

    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.isdigit():
            raise ValueError('Phone number must contain only digits')
        return v

    @validator('nid_number')
    def validate_nid_number(cls, v):
        if v and not v.isalnum():
            raise ValueError('NID number must be alphanumeric')
        return v

class ShopRenterProfileCreate(ShopRenterProfileBase):
    # Additional fields specific to creation
    nid_front: Optional[bytes] = None
    nid_back: Optional[bytes] = None
    documents: Optional[bytes] = None

class ShopRenterProfileUpdate(ShopRenterProfileBase):
    # Fields that can be updated
    pass

class ShopRenterProfileResponse(ShopRenterProfileBase):
    id: int
    created_at: Optional[datetime] = None
    update_at: Optional[datetime] = None

    class Config:
        orm_mode = True
