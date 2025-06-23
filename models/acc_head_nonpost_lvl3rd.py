from sqlalchemy import Column, Integer, String
from .base import Base

class AccHeadNonpostLvl3rd(Base):
    __tablename__ = 'acc_head_nonpost_lvl3rd'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    head_acc_id = Column(Integer, nullable=False)
    head_name = Column(String(50))