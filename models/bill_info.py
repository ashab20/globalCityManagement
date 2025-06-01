from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from .base import Base
from sqlalchemy.orm import relationship
from utils.database import Session

class BillInfo(Base):
    __tablename__ = 'bill_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    # shop_id = Column(Integer, nullable=True)
    shop_id = Column(Integer, ForeignKey('shop_profile.id'), nullable=True)
    owner_id = Column(Integer, nullable=True)
    bill_year = Column(Integer, nullable=True)
    bill_month = Column(Integer, nullable=True)
    bill_date = Column(DateTime, nullable=True)
    bill_amount = Column(DECIMAL(10,2), nullable=True)
    prev_due = Column(DECIMAL(10,2), nullable=True)
    elect_op_unit = Column(DECIMAL(10,2), nullable=True)
    elect_closing_unit = Column(DECIMAL(10,2), nullable=True)
    gas_op_unit = Column(DECIMAL(10,2), nullable=True)
    gas_closing_unit = Column(DECIMAL(10,2), nullable=True)
    wasa_op_unit = Column(DECIMAL(10,2), nullable=True)
    wasa_closing_unit = Column(DECIMAL(10,2), nullable=True)
    last_pay_date = Column(DateTime, nullable=True)
    pay_amount = Column(DECIMAL(10,2), nullable=True)
    cur_due = Column(DECIMAL(10,2), nullable=True)
    bill_gen_by = Column(String(20), nullable=True)
    bill_gen_at = Column(DateTime, nullable=True)
    status = Column(Integer, nullable=True)
    
    
    # shop = relationship("ShopProfile", back_populates="bills")
    # shop = relationship("ShopProfile", back_populates="bills")
    # particulars = relationship("BillParticular", 
    #                          back_populates="bill",
    #                          cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BillInfo(id={self.id}, shop_id={self.shop_id}, bill_amount={self.bill_amount}, status={self.status})>"

    @classmethod
    def get_bill_by_id(cls, id):
        session = Session()
        try:
            return session.query(cls).filter_by(id=id).first()
        finally:
            session.close()

    @classmethod
    def get_bill_by_shop_id(cls, shop_id):
        session = Session()
        try:
            return session.query(cls).filter_by(shop_id=shop_id).all()
        finally:
            session.close()