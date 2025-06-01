from sqlalchemy import Column, Integer, String
from .base import Base

class AccHeadNonpostLvl4rd(Base):
    __tablename__ = 'acc_head_nonpost_lvl4rd'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    head_lvl3rd_id = Column(Integer, nullable=False)
    head_name = Column(String(50))