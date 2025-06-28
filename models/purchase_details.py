from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from utils.database import Base

class PurchaseDetails(Base):
    __tablename__ = "purchase_details"
    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, ForeignKey("product_purchase.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=True)
    quantity = Column(Integer, nullable=True)
    unit_price = Column(Integer, nullable=True)
    total = Column(Integer, nullable=True)

    # Relationships
    purchase = relationship("ProductPurchase", back_populates="purchase_details")
    product = relationship("Product", back_populates="purchase_details")

    def __repr__(self):
        return f"<PurchaseDetails(id={self.id}, purchase_id='{self.purchase_id}', product_id='{self.product_id}', quantity='{self.quantity}', unit_price='{self.unit_price}', total='{self.total}')>"
    
    