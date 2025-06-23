from .base import Base
from sqlalchemy import Column, Integer, String, DECIMAL
from utils.database import Session

class UtilitySetting(Base):
    __tablename__ = 'utility_setting'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    utility_name = Column(String(150))
    utility_unit = Column(String(50))
    utility_rate = Column(DECIMAL(10,2))
    releted_head_id = Column(Integer)
    vat = Column(DECIMAL(10,2), nullable=True,default=0)
    demand_charge = Column(DECIMAL(10,2), nullable=True,default=0)
    remarks = Column(String(255))

    @staticmethod
    def get_utility_setting(head_id):
        session = Session()
        try:
            return session.query(UtilitySetting).filter_by(releted_head_id=head_id).first()
        finally:
            session.close()
    
    @staticmethod
    def get_all_utility_setting():
        session = Session()
        try:
            return session.query(UtilitySetting).all()
        finally:
            session.close()
    
    @staticmethod
    def get_utility_setting_by_id(id):
        session = Session()
        try:
            return session.query(UtilitySetting).get(id)
        finally:
            session.close()

    @staticmethod
    def get_unit_price(head_id):
        session = Session()
        try:
            utility_setting = session.query(UtilitySetting).filter_by(releted_head_id=head_id).first()
            if utility_setting:
                return {
                    "unit_price": float(utility_setting.utility_rate),
                    "unit": utility_setting.utility_unit,
                    "vat": float(utility_setting.vat),
                    "demand_charge": float(utility_setting.demand_charge)
                }
            return {"unit_price": 0.0, "unit": "", "vat": 0.0, "demand_charge": 0.0}
        except Exception as e:
            print(f"Error getting unit price: {str(e)}")
            return {"unit_price": 0.0, "unit": "", "vat": 0.0, "demand_charge": 0.0}
        finally:
            session.close()