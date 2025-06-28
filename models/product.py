from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from utils.database import Base

class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("category.id"))
    unit_id = Column(Integer, ForeignKey("unit.id"))
    name = Column(String(100))
    description = Column(String(255), nullable=True)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

    # Relationships
    category = relationship("Category", back_populates="products")
    unit = relationship("Unit", back_populates="products")
    purchase_details = relationship("PurchaseDetails", back_populates="product")
    demand_details = relationship("DemandDetails", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', status={self.status})>"
    
    @classmethod
    def get_all(cls):
        return cls.query.filter_by(status=1).all()
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id, status=1).first()
    
    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name, status=1).first()
    