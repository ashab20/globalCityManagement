from sqlalchemy.orm import Session
from models.shop_renter_profile import ShopRenterProfile
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any

class ShopRenterProfileController:
    @staticmethod
    def create(db: Session, shop_renter_profile_data: Dict[str, Any]) -> ShopRenterProfile:
        """
        Create a new shop renter profile
        
        :param db: Database session
        :param shop_renter_profile_data: Dictionary of profile data
        :return: Created ShopRenterProfile instance
        """
        try:
            new_profile = ShopRenterProfile(**shop_renter_profile_data)
            db.add(new_profile)
            db.commit()
            db.refresh(new_profile)
            return new_profile
        except SQLAlchemyError as e:
            db.rollback()
            raise ValueError(f"Error creating shop renter profile: {str(e)}")

    @staticmethod
    def get_by_id(db: Session, profile_id: int) -> Optional[ShopRenterProfile]:
        """
        Retrieve a shop renter profile by its ID
        
        :param db: Database session
        :param profile_id: ID of the profile
        :return: ShopRenterProfile instance or None
        """
        return db.query(ShopRenterProfile).filter(ShopRenterProfile.id == profile_id).first()

    @staticmethod
    def get_all(db: Session, active_only: bool = True) -> List[ShopRenterProfile]:
        """
        Retrieve all shop renter profiles
        
        :param db: Database session
        :param active_only: Flag to return only active profiles
        :return: List of ShopRenterProfile instances
        """
        query = db.query(ShopRenterProfile)
        if active_only:
            query = query.filter(ShopRenterProfile.active_status == 1)
        return query.all()

    @staticmethod
    def update(db: Session, profile_id: int, update_data: Dict[str, Any]) -> Optional[ShopRenterProfile]:
        """
        Update an existing shop renter profile
        
        :param db: Database session
        :param profile_id: ID of the profile to update
        :param update_data: Dictionary of fields to update
        :return: Updated ShopRenterProfile instance or None
        """
        try:
            profile = db.query(ShopRenterProfile).filter(ShopRenterProfile.id == profile_id).first()
            if not profile:
                return None
            
            for key, value in update_data.items():
                setattr(profile, key, value)
            
            db.commit()
            db.refresh(profile)
            return profile
        except SQLAlchemyError as e:
            db.rollback()
            raise ValueError(f"Error updating shop renter profile: {str(e)}")

    @staticmethod
    def delete(db: Session, profile_id: int) -> bool:
        """
        Soft delete a shop renter profile by setting active_status to 0
        
        :param db: Database session
        :param profile_id: ID of the profile to delete
        :return: Boolean indicating success of deletion
        """
        try:
            profile = db.query(ShopRenterProfile).filter(ShopRenterProfile.id == profile_id).first()
            if not profile:
                return False
            
            profile.active_status = 0  # Soft delete
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise ValueError(f"Error deleting shop renter profile: {str(e)}")
