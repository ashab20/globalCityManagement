from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from utils.database import Base
from datetime import datetime

class Unit(Base):
    __tablename__ = "unit"
    id = Column(Integer, primary_key=True)
    unit_name = Column(String(100))
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

    # Relationships
    products = relationship("Product", back_populates="unit")

    def __repr__(self):
        return f"<Unit(id={self.id}, name='{self.unit_name}', status={self.status})>"
    
    @classmethod
    def get_all(cls):
        return cls.query.filter_by(status=1).all()
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id, status=1).first()
    
    @classmethod
    def get_by_name(cls, unit_name):
        return cls.query.filter_by(unit_name=unit_name, status=1).first()
    