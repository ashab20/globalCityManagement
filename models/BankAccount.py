from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from .base import Base

class BankAccount(Base):
    __tablename__ = 'bank_account'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_name = Column(String(50))
    account_no = Column(String(50))
    status = Column(Integer, default=0)
    entry_by = Column(String(30))
    entry_time = Column(DateTime)