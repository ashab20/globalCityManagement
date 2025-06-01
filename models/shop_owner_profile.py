from sqlalchemy import Column, Integer, String, DateTime, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class ShopOwnerProfile(Base):
    __tablename__ = 'shop_ownner_profile'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ownner_name = Column(String(50), nullable=True)
    phone = Column(String(15), nullable=True)
    email = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    nid_number = Column(String(20), nullable=True)
    nid_front = Column(LargeBinary, nullable=True)
    nid_back = Column(LargeBinary, nullable=True)
    photo = Column(LargeBinary, nullable=True)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    update_by = Column(Integer, nullable=True)
    update_at = Column(DateTime, onupdate=func.now(), nullable=True)
    active_status = Column(Integer, default=1, nullable=True)  # 1 = active

    # Relationships
    # shops = relationship("ShopProfile", back_populates="owner")

    def __repr__(self):
        return f"<ShopOwnerProfile(id={self.id}, name='{self.ownner_name}', email='{self.email}')>"
