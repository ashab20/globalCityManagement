from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class ShopProfile(Base):
    __tablename__ = 'shop_profile'

    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_owner_id = Column(Integer, ForeignKey('shop_ownner_profile.id'), nullable=False)
    floor_no = Column(String(100), nullable=False)
    shop_no = Column(String(100), nullable=False)
    shop_name = Column(String(100), nullable=False)
    rent_type = Column(String(100), nullable=False)
    shop_size = Column(Numeric(10,2), nullable=False)
    per_sqr_fit_amt = Column(Numeric(10,2), nullable=False)
    descreption = Column(String(255), nullable=False)
    rent_amout = Column(Numeric(10, 2), nullable=True)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    update_by = Column(Integer, nullable=True)
    update_at = Column(DateTime, onupdate=func.now(), nullable=True)
    active_status = Column(Integer, default=1, nullable=True)  # 1 = active

    # Relationships
    # owner = relationship("ShopOwnerProfile", back_populates="shops")
    # allocations = relationship("ShopAllocation", back_populates="shop_profile")

    def __repr__(self):
        return f"<ShopProfile(id={self.id}, name='{self.shop_name}', floor_no='{self.floor_no}')>"


# ALTER TABLE `db_globalcity`.`shop_profile` ADD COLUMN `rent_type` VARCHAR(20) NULL AFTER `descreption`, ADD COLUMN `shop_size` DECIMAL(10,2) NULL COMMENT 'square fit' AFTER `rent_type`, ADD COLUMN `per_sqr_fit_amt` DECIMAL(10,2) NULL AFTER `shop_size`; 