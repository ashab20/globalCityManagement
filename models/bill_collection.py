from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from .base import Base
from sqlalchemy.orm import relationship
from utils.database import Session

class BillCollection(Base):
    __tablename__ = 'bill_collection'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_id = Column(Integer, ForeignKey('shop_profile.id'), nullable=False)
    bill_id = Column(Integer, ForeignKey('bill_info.id'), nullable=False)
    bank_id = Column(Integer, ForeignKey('bank_account.id'), nullable=True)
    trans_date = Column(DateTime, nullable=False)
    trans_mode = Column(String(20), nullable=False)
    check_no = Column(String(20), nullable=True)
    trans_amount = Column(DECIMAL(10,2), nullable=False)
    pay_amount = Column(DECIMAL(10,2), nullable=True)
    due_amount = Column(DECIMAL(10,2), nullable=True)
    remarks = Column(String(255), nullable=True)
    
    # shop = relationship("ShopProfile", back_populates="bill_collections")
    # bill = relationship("BillInfo", back_populates="bill_collections")

    shop = relationship("ShopProfile")
    bill = relationship("BillInfo")
    bank = relationship("BankAccount")



    def get_collection_by_id(cls, id):
        session = Session()
        try:
            return session.query(cls).filter_by(id=id).first()
        finally:
            session.close()

    @classmethod
    def get_collection_by_shop_id(cls, shop_id):
        session = Session()
        try:
            return session.query(cls).filter_by(shop_id=shop_id).all()
        finally:
            session.close()
    