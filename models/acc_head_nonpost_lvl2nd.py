from sqlalchemy import Column, Integer, String
from .base import Base

class AccHeadNonpostLvl2nd(Base):
    __tablename__ = 'acc_head_nonpost_lvl2nd'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chart_acc_id = Column(Integer, nullable=False)
    head_name = Column(String(50))