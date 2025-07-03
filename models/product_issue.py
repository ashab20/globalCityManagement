from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from utils.database import Base
from datetime import datetime

class ProductIssue(Base):
    __tablename__ = "product_issue"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=True)
    qty = Column(Integer, nullable=True)
    issue_date = Column(DateTime, nullable=True)
    issue_no = Column(String(50), nullable=True)
    remark = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(Integer, default=1)

    # Relationships
    products = relationship("Product", back_populates="unit")

    def __repr__(self):
        return f"<Unit(id={self.id}, name='{self.unit_name}', status={self.status})>"
    
    @classmethod
    def get_all(cls):
        return cls.query.filter_by(status=1).all()
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id, status=1).first()
    
    @classmethod
    def get_by_name(cls, unit_name):
        return cls.query.filter_by(unit_name=unit_name, status=1).first()
    