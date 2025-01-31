from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from controllers.shop_profile_controller import ShopProfileController
from schemas.shop_profile_schema import ShopProfileCreate, ShopProfileUpdate, ShopProfileResponse
from utils.database import get_db

router = APIRouter(prefix="/shop-profile", tags=["Shop Profile"])

@router.post("/", response_model=ShopProfileResponse)
def create_shop_profile(
    profile: ShopProfileCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new shop profile
    """
    try:
        return ShopProfileController.create(db, profile)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ShopProfileResponse])
def get_all_shop_profiles(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Retrieve all shop profiles
    """
    return ShopProfileController.get_all(db, active_only)

@router.get("/{profile_id}", response_model=ShopProfileResponse)
def get_shop_profile(
    profile_id: int, 
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific shop profile by ID
    """
    shop_profile = ShopProfileController.get_by_id(db, profile_id)
    if not shop_profile:
        raise HTTPException(status_code=404, detail="Shop profile not found")
    return shop_profile

@router.put("/{profile_id}", response_model=ShopProfileResponse)
def update_shop_profile(
    profile_id: int, 
    profile_update: ShopProfileUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing shop profile
    """
    updated_profile = ShopProfileController.update(db, profile_id, profile_update)
    if not updated_profile:
        raise HTTPException(status_code=404, detail="Shop profile not found")
    return updated_profile

@router.delete("/{profile_id}", response_model=dict)
def delete_shop_profile(
    profile_id: int, 
    db: Session = Depends(get_db)
):
    """
    Soft delete a shop profile
    """
    deletion_result = ShopProfileController.delete(db, profile_id)
    if not deletion_result:
        raise HTTPException(status_code=404, detail="Shop profile not found")
    return {"message": "Shop profile successfully deleted"}
