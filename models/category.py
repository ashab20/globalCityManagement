from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from utils.database import Base
from datetime import datetime

class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(String(255), nullable=True)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

    # Relationships
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', status={self.status})>"
    
    @classmethod
    def get_all(cls):
        return cls.query.filter_by(status=1).all()
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id, status=1).first()
    
    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name, status=1).first()
    