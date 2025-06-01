from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from .base import Base
from utils.database import Session

class AccHeadOfAccounts(Base):
    __tablename__ = 'acc_head_of_accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    head_lvl4th_id = Column(Integer)
    head_name = Column(String(50))
    remarks = Column(String(250))
    bank_id = Column(Integer)
    isActive = Column(Integer,default=0)
    entry_by = Column(Integer)
    entry_time = Column(DateTime)
    change_by = Column(Integer)
    change_time = Column(DateTime)
    status = Column(Integer, default=0)

    @staticmethod
    def get_head_of_accounts(session: Session):
        return session.query(AccHeadOfAccounts).all()