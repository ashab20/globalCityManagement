from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

class ShopProfileBase(BaseModel):
    floor_no: str = Field(..., description="Floor number of the shop")
    shop_no: str = Field(..., description="Shop number")
    shop_name: str = Field(..., description="Name of the shop")
    descreption: Optional[str] = Field(None, description="Shop description")
    rent_amout: Optional[Decimal] = Field(None, description="Rent amount")
    shop_owner_id: int = Field(..., description="ID of the shop owner")
    active_status: Optional[int] = Field(1, description="Active status of the shop")

class ShopProfileCreate(ShopProfileBase):
    pass

class ShopProfileUpdate(BaseModel):
    floor_no: Optional[str] = None
    shop_no: Optional[str] = None
    shop_name: Optional[str] = None
    descreption: Optional[str] = None
    rent_amout: Optional[Decimal] = None
    active_status: Optional[int] = None

class ShopProfileResponse(ShopProfileBase):
    id: int
    created_at: Optional[datetime] = None
    update_at: Optional[datetime] = None

    class Config:
        from_attributes = True
