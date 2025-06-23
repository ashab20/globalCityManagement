from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from .base import Base

class Particular(Base):
    __tablename__ = 'particular'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    unit = Column(String(50))