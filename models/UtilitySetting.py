from .base import Base
from sqlalchemy import Column, Integer, String, DECIMAL


class UtilitySetting(Base):
    __tablename__ = 'ustility_setting'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    utility_name = Column(String(150))
    utility_rate = Column(DECIMAL(10,2))
    remarks = Column(String(255))