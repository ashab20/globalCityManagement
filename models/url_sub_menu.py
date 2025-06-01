from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from .base import Base

class UrlSubMenu(Base):
    __tablename__ = 'url_sub_menu'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    top_menu_id = Column(Integer)
    sub_menu_order = Column(String(50))
    sub_menu_name  = Column(String(50))
    command_name = Column(Integer)
    # status = Column(Integer, default=0)