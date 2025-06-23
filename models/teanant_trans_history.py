from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from .base import Base

class TeanantTransHistory(Base):
    __tablename__ = 'teanant_trans_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    teanant_id = Column(Integer, nullable=True)
    bill_info_id = Column(Integer, nullable=True)
    collect_id = Column(Integer, nullable=True)
    trans_dt = Column(DateTime, nullable=True)
    trans_amount = Column(DECIMAL(10, 2), nullable=True)
    crdr_type = Column(String(2), nullable=True)
    closing_amt = Column(String(255), nullable=True)
    closing_crdr_type = Column(String(2), nullable=True)
    remarks = Column(String(255), nullable=True)
    entry_time = Column(DateTime, nullable=True)
    entry_user = Column(String(50), nullable=True)