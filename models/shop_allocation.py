from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class ShopAllocation(Base):
    __tablename__ = 'shop_allocation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_profile_id = Column(Integer, ForeignKey('shop_profile.id'), nullable=True)
    renter_profile_id = Column(Integer, ForeignKey('shop_renter_profile.id'), nullable=True)
    from_year = Column(Integer, nullable=True)
    from_month = Column(Integer, nullable=True)
    to_year = Column(Integer, nullable=True)
    to_month = Column(Integer, nullable=True)
    close_status = Column(Integer, default=0, nullable=True)  # 0=active, 1=close
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    update_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    update_at = Column(DateTime, onupdate=func.now(), nullable=True)

    # Relationships
    # shop_profile = relationship("ShopProfile", back_populates="allocations")
    # renter_profile = relationship("ShopRenterProfile", back_populates="allocations")
    # creator = relationship("User", foreign_keys=[created_by])
    # updater = relationship("User", foreign_keys=[update_by])

    def __repr__(self):
        return f"<ShopAllocation(id={self.id}, shop_profile_id={self.shop_profile_id}, renter_profile_id={self.renter_profile_id})>"

    @classmethod
    def get_renter_profile_by_shop_id(cls, session, shop_id, year=None, month=None):
        """Get renter profile by shop_id"""
        try:
            # query = session.query(cls).filter_by(shop_profile_id=shop_id, from_year=year, from_month=month).first()
            query = session.query(cls).filter_by(shop_profile_id=shop_id).first()
            return query
        except Exception as e:
            print(f"Error getting renter profile by shop_id: {str(e)}")
            return None
