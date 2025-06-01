from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
from utils.database import Session



class ShopProfile(Base):
    __tablename__ = 'shop_profile'

    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_owner_id = Column(Integer, ForeignKey('shop_ownner_profile.id'), nullable=False)
    floor_no = Column(String(100), nullable=False)
    shop_no = Column(String(100), nullable=True)
    shop_name = Column(String(100), nullable=False)
    rent_type = Column(String(100), nullable=True)
    shop_size = Column(Numeric(10,2), nullable=True)
    per_sqr_fit_amt = Column(Numeric(10,2), nullable=True)
    descreption = Column(String(255), nullable=True)
    rent_amount = Column(Numeric(10, 2), nullable=True)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    update_by = Column(Integer, nullable=True)
    update_at = Column(DateTime, onupdate=func.now(), nullable=True)
    active_status = Column(Integer, default=1, nullable=True)  # 1 = active
    elect_demand_chrge = Column(Numeric(10, 2), nullable=True)
    internet_bill = Column(Numeric(10, 2), nullable=True)

    # Relationships
    # owner = relationship("ShopOwnerProfile", back_populates="shops")
    # allocations = relationship("ShopAllocation", back_populates="shop_profile")
    # bills = relationship("BillInfo", back_populates="shop")
    # bills = relationship("BillInfo", back_populates="shop", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ShopProfile(id={self.id}, name='{self.shop_name}', floor_no='{self.floor_no}')>"
    
    @classmethod
    def get_shop_info(cls, shop_id):
        """Get shop information by shop_id"""
        try:
            session = Session()
            shop = session.query(cls).filter_by(id=shop_id).first()
            return shop
        except Exception as e:
            print(f"Error getting shop info: {str(e)}")
            return None
        finally:
            session.close()

