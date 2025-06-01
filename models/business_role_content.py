from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from .base import Base

class BusinessRoleContent(Base):
    __tablename__ = 'business_role_content'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_role_id = Column(Integer)
    sub_menu_id = Column(Integer)