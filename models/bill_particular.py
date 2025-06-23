from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from .base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
class BillParticular(Base):
    __tablename__ = 'bill_particular'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    # bill_id = Column(Integer, nullable=True)
    bill_id = Column(Integer, nullable=False)
    bill_particular = Column(String(200), nullable=True)
    bill_qty = Column(DECIMAL(10,2), nullable=True)
    bill_unit = Column(String(20), nullable=True)
    bill_rate = Column(DECIMAL(10,2), nullable=True)
    sub_amount = Column(DECIMAL(10,2), nullable=True)
    paid_amount = Column(DECIMAL(10,2), nullable=True)
    due_amount = Column(DECIMAL(10,2), nullable=True)
    bill_collection_id = Column(Integer, nullable=True)
    vat = Column(DECIMAL(10,2), nullable=True,default=0)
    demand_charge = Column(DECIMAL(10,2), nullable=True,default=0)
    bill_type = Column(String(20), nullable=True,default="Bill",comment="Bill, Collection") # Bill, Collection
    # bill = relationship("BillInfo", back_populates="particulars")


    @staticmethod
    def get_bill_particular_by_bill_id(session: Session, bill_id: int):
        return session.query(BillParticular) \
            .filter(BillParticular.bill_id == bill_id, BillParticular.bill_type == "Bill") \
            .all()
    
    @staticmethod
    def get_bill_particular_by_bill_collection_id(session: Session, bill_collection_id: int):
        return session.query(BillParticular) \
            .filter(BillParticular.bill_collection_id == bill_collection_id, BillParticular.bill_type == "Collection") \
            .all()
    
    
    