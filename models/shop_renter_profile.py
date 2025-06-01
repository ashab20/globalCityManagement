from sqlalchemy import Column, Integer, String, DateTime, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class ShopRenterProfile(Base):
    __tablename__ = 'shop_renter_profile'

    id = Column(Integer, primary_key=True, autoincrement=True)
    renter_name = Column(String(50), nullable=True)
    phone = Column(String(15), nullable=True)
    email = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    nid_number = Column(String(20), nullable=True)
    nid_front = Column(LargeBinary, nullable=True)
    nid_back = Column(LargeBinary, nullable=True)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    update_by = Column(Integer, nullable=True)
    update_at = Column(DateTime, onupdate=func.now(), nullable=True)
    active_status = Column(Integer, default=1, nullable=True)  # 1 = active
    documents = Column(LargeBinary, nullable=True)

    # Relationships
    # allocations = relationship("ShopAllocation", back_populates="renter_profile")

    def __repr__(self):
        return f"<ShopRenterProfile(id={self.id}, name='{self.renter_name}', email='{self.email}')>"
