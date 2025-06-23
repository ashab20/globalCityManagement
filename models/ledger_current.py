from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from .base import Base

class LedgerCurrent(Base):
    __tablename__ = 'ledger_current'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(DECIMAL(10,2))
    head_id = Column(String(50))
    branch_id = Column(Integer)
    drcr_type = Column(String(2))