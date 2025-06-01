from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from .base import Base

class BusinessRoleModifier(Base):
    __tablename__ = 'business_role_modifier'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    modifier_name= Column(String(50))