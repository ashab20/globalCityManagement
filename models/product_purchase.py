from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from utils.database import Base

class ProductPurchase(Base):
    __tablename__ = "product_purchase"
    id = Column(Integer, primary_key=True)
    purchase_date = Column(DateTime, nullable=True)
    purchase_no = Column(String(50), nullable=True)
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
    shop = relationship("ShopProfile", back_populates="product_purchases")
    purchase_details = relationship("PurchaseDetails", back_populates="purchase")

    def __repr__(self):
        return f"<ProductPurchase(id={self.id}, purchase_no='{self.purchase_no}', status={self.status})>"
    
    @classmethod
    def get_all(cls):
        return cls.query.filter_by(status=1).all()
    
