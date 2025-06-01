from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from .base import Base
from sqlalchemy.orm import relationship

class BillCollection(Base):
    __tablename__ = 'bill_collection'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_id = Column(Integer, nullable=False)
    bill_id = Column(Integer, nullable=False)
    trans_date = Column(DateTime, nullable=False)
    trans_mode = Column(String(20), nullable=False)
    bank_id = Column(Integer,nullable=True)
    check_no = Column(String(20), nullable=True)
    trans_amount = Column(DECIMAL(10,2), nullable=False)
    pay_amount = Column(DECIMAL(10,2), nullable=True)
    due_amount = Column(DECIMAL(10,2), nullable=True)
    remarks = Column(String(255), nullable=True)
    
    # shop = relationship("ShopProfile", back_populates="bill_collections")
    # bill = relationship("BillInfo", back_populates="bill_collections")
    