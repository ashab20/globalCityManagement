
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from utils.database import Base

class DemandDetails(Base):
    __tablename__ = "demand_details"
    id = Column(Integer, primary_key=True)
    demand_id = Column(Integer, ForeignKey("demand_product.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    quantity = Column(Integer)
    unit_price = Column(Integer)
    total = Column(Integer)

    demand_product = relationship("DemandProduct", back_populates="demand_details")
    product = relationship("Product", back_populates="demand_details")

    def __repr__(self):
        return f"<DemandDetails(id={self.id}, demand_id='{self.demand_id}', product_id='{self.product_id}', quantity='{self.quantity}', unit_price='{self.unit_price}', total='{self.total}')>"
    
    
    @classmethod
    def get_by_demand_id(cls, demand_id):
        return cls.query.filter_by(demand_id=demand_id, status=1).all()
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id, status=1).first()
    
    @classmethod
    def get_by_product_id(cls, product_id):
        return cls.query.filter_by(product_id=product_id, status=1).all()