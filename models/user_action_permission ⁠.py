from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from .base import Base

class UserActionPermission(Base):
    __tablename__ = 'user_action_permission'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id= Column(Integer)
    user_role_id = Column(Integer)
    sub_menu_id = Column(Integer)