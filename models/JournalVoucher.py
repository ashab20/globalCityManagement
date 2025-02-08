from .base import Base
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey

class JournalVoucher(Base):
    __tablename__ = 'journal_voucher'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    head_id = Column(Integer, nullable=False)  # Update 'some_table.id' with the actual referenced table
    trans_type = Column(String(20), nullable=False)
    trans_mode = Column(String(20))
    trans_date = Column(String(100))
    trans_amount = Column(DECIMAL(10,2))
    remarks = Column(String(200), nullable=False)
    entry_by = Column(String(15), nullable=False)
    entry_time = Column(DateTime, nullable=False)
    bank_acc_id = Column(String(80), nullable=False)
    cheque_no = Column(String(50))