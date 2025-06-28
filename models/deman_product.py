from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from utils.database import Base
from datetime import datetime

class DemandProduct(Base):
    __tablename__ = "demand_product"
    id = Column(Integer, primary_key=True)
    demand_date = Column(DateTime, default=datetime.now)
    demand_no = Column(String(50), nullable=True)
    shop_id = Column(Integer, ForeignKey("shop_profile.id"), nullable=True)
    sub_total = Column(Integer, nullable=True)
    discount = Column(Integer, nullable=True)
    grand_total = Column(Integer, nullable=True)
    status = Column(Integer, default=1)
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approved_status = Column(Integer, default=0)
    approved_note = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

    # Relationships
    shop = relationship("ShopProfile", back_populates="demand_products")
    demand_details = relationship("DemandDetails", back_populates="demand_product")

    def __repr__(self):
        return f"<DemandProduct(id={self.id}, demand_no='{self.demand_no}', status={self.status})>"
    
    @classmethod
    def get_all(cls):
        return cls.query.filter_by(status=1).all()
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id, status=1).first()