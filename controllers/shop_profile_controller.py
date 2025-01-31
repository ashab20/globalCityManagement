from sqlalchemy.orm import Session
from models.shop_profile import ShopProfile
from schemas.shop_profile_schema import ShopProfileCreate, ShopProfileUpdate
from typing import List, Optional

class ShopProfileController:
    @staticmethod
    def create(db: Session, shop_profile: ShopProfileCreate) -> ShopProfile:
        """
        Create a new shop profile
        """
        db_shop_profile = ShopProfile(**shop_profile.model_dump())
        db.add(db_shop_profile)
        db.commit()
        db.refresh(db_shop_profile)
        return db_shop_profile

    @staticmethod
    def get_all(db: Session, active_only: bool = True) -> List[ShopProfile]:
        """
        Retrieve all shop profiles, optionally filtering by active status
        """
        query = db.query(ShopProfile)
        if active_only:
            query = query.filter(ShopProfile.active_status == 1)
        return query.all()

    @staticmethod
    def get_by_id(db: Session, profile_id: int) -> Optional[ShopProfile]:
        """
        Retrieve a specific shop profile by ID
        """
        return db.query(ShopProfile).filter(ShopProfile.id == profile_id).first()

    @staticmethod
    def update(db: Session, profile_id: int, profile_update: ShopProfileUpdate) -> Optional[ShopProfile]:
        """
        Update an existing shop profile
        """
        db_shop_profile = db.query(ShopProfile).filter(ShopProfile.id == profile_id).first()
        if not db_shop_profile:
            return None

        update_data = profile_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_shop_profile, key, value)

        db.commit()
        db.refresh(db_shop_profile)
        return db_shop_profile

    @staticmethod
    def delete(db: Session, profile_id: int) -> bool:
        """
        Soft delete a shop profile by setting active_status to 0
        """
        db_shop_profile = db.query(ShopProfile).filter(ShopProfile.id == profile_id).first()
        if not db_shop_profile:
            return False

        db_shop_profile.active_status = 0
        db.commit()
        return True
