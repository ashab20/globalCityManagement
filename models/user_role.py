from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class UserRole(Base):
    __tablename__ = 'user_roles'  # Changed to plural to match foreign key

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    # Relationships
    users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<UserRole(id={self.id}, name='{self.name}')>"
