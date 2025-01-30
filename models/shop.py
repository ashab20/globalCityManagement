from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base
from models.renter import Renter



class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, autoincrement=True)
    shopName = Column(String(100), nullable=False, unique=False)
    floorNo = Column(String(100), nullable=False, unique=False)
    shopNo = Column(String(100), nullable=False, unique=False)
    address = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    # owner = relationship("User", back_populates="shops")
    # renters = relationship("Renter", back_populates="shop", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Shop(id={self.id}, name='{self.name}', address='{self.address}', owner_id={self.owner_id})>"
