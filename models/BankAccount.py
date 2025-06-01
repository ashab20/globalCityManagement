from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from .base import Base
from utils.database import Session


class BankAccount(Base):
    __tablename__ = 'bank_account'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_name = Column(String(50))
    account_no = Column(String(50))
    status = Column(Integer, default=0)
    entry_by = Column(String(30))
    entry_time = Column(DateTime)
    
    @staticmethod
    def get_banks():
        session = Session()
        try:
            return (
                session.query(BankAccount)
                .filter_by(status=1)
                .all()
            )
        finally:
            session.close()