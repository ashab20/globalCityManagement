from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from .base import Base

class AccountJournal(Base):
    __tablename__ = 'account_journal'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    head_id = Column(Integer)
    bill_info_id = Column(Integer, nullable=True)
    bill_colct_id = Column(Integer, nullable=True)
    trans_date = Column(DateTime, nullable=True)
    amount = Column(DECIMAL(10,2), nullable=True)
    drcr_type = Column(String(2),nullable=True)
    transaction_ref = Column(Integer,nullable=True)
    jrnlVocr_ref_id = Column(Integer,nullable=True)
    remarks = Column(String(200),nullable=True)
    # status = Column(Integer, default=0)
    entry_by = Column(String(30),nullable=True)
    entry_time = Column(DateTime,nullable=True )