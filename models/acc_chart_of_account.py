from sqlalchemy import Column, Integer, String
from .base import Base

class AccChartOfAccount(Base):
    __tablename__ = 'acc_chart_of_account'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    head_type_name = Column(String(50))