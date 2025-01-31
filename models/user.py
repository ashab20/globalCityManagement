from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from utils.database import Session
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    login_id = Column(String(50), unique=True, nullable=False)
    usr_full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("user_roles.id"), nullable=False)
    avatar = Column(LargeBinary, nullable=True)
    ptext = Column(String(255), nullable=True)
    created_by = Column(Integer, nullable=True)
    update_by = Column(Integer, nullable=True)
    active_status = Column(Integer, default=1, nullable=True)  # 1 = active, 0 = deactive
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    role = relationship("UserRole", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, login_id='{self.login_id}', email='{self.email}')>"

    @classmethod
    def find_by_username(cls, login_id):
        """Find a user by their login ID."""
        session = Session()
        try:
            user = session.query(cls).filter(cls.login_id == login_id).first()
            return user
        finally:
            session.close()
