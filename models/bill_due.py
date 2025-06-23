from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from .base import Base
from sqlalchemy.orm import relationship

class BillDue(Base):
    __tablename__ = 'bill_due'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_id = Column(Integer, nullable=False)
    due_amount = Column(DECIMAL(10,2), nullable=True)
    
    # shop = relationship("Shop", back_populates="bill_dues")
    