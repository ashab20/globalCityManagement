from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base

class Renter(Base):
    __tablename__ = 'renters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    shop_id = Column(Integer, ForeignKey('shops.id'), nullable=False)
    
    # Relationships
    # shop = relationship("Shop", back_populates="renters")
