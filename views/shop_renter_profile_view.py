from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional

from controllers.shop_renter_profile_controller import ShopRenterProfileController
from database import get_db
from models.shop_renter_profile import ShopRenterProfile
from schemas.shop_renter_profile_schema import ShopRenterProfileCreate, ShopRenterProfileUpdate, ShopRenterProfileResponse

router = APIRouter(prefix="/shop-renter-profile", tags=["Shop Renter Profile"])

@router.post("/", response_model=ShopRenterProfileResponse)
def create_shop_renter_profile(
    profile: ShopRenterProfileCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new shop renter profile
    """
    try:
        # Convert Pydantic model to dictionary, excluding None values
        profile_data = {k: v for k, v in profile.dict().items() if v is not None}
        new_profile = ShopRenterProfileController.create(db, profile_data)
        return new_profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ShopRenterProfileResponse])
def get_all_shop_renter_profiles(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Retrieve all shop renter profiles
    """
    profiles = ShopRenterProfileController.get_all(db, active_only)
    return profiles

@router.get("/{profile_id}", response_model=ShopRenterProfileResponse)
def get_shop_renter_profile(
    profile_id: int, 
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific shop renter profile by ID
    """
    profile = ShopRenterProfileController.get_by_id(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Shop renter profile not found")
    return profile

@router.put("/{profile_id}", response_model=ShopRenterProfileResponse)
def update_shop_renter_profile(
    profile_id: int, 
    profile_update: ShopRenterProfileUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing shop renter profile
    """
    # Convert Pydantic model to dictionary, excluding None values
    update_data = {k: v for k, v in profile_update.dict().items() if v is not None}
    
    try:
        updated_profile = ShopRenterProfileController.update(db, profile_id, update_data)
        if not updated_profile:
            raise HTTPException(status_code=404, detail="Shop renter profile not found")
        return updated_profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{profile_id}", response_model=dict)
def delete_shop_renter_profile(
    profile_id: int, 
    db: Session = Depends(get_db)
):
    """
    Soft delete a shop renter profile
    """
    try:
        deletion_result = ShopRenterProfileController.delete(db, profile_id)
        if not deletion_result:
            raise HTTPException(status_code=404, detail="Shop renter profile not found")
        return {"message": "Shop renter profile successfully deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while deleting shop renter profile: {str(e)}")
