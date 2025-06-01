from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from .base import Base

class UrlTopMenu(Base):
    __tablename__ = 'url_top_menu'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_name = Column(String(50))
    menu_order = Column(Integer)
    # status = Column(Integer, default=0)