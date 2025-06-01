from .base import Base
from sqlalchemy import Column, Integer, String, DateTime

class ProductSupplier(Base):
    __tablename__ = 'product_suplier'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_name = Column(String(150), nullable=False, default='')
    address = Column(String(100), nullable=False)
    contact_no = Column(String(100), nullable=False)
    deed = Column(String(250))
    is_active = Column(Integer, nullable=False, default=1)
    is_manufacturer = Column(Integer, default=0)  # 0=supplier, 1=supplier+manufacturer
    entry_user = Column(String(50), nullable=False)
    entry_time = Column(DateTime)