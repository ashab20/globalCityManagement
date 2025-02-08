from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, LargeBinary, Boolean
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy.sql import func
from utils.database import Session
from .base import Base
from datetime import datetime

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
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    role = relationship("UserRole", back_populates="users", lazy="joined")

    def __repr__(self):
        return f"<User(id={self.id}, login_id='{self.login_id}', email='{self.email}', role='{self.get_role_name()}')>"

    def get_role_name(self):
        """
        Get the name of the user's role.
        
        :return: Role name as a string, default to 'staff' if no role
        """
        try:
            return self.role.name if self.role else 'staff'
        except Exception:
            return 'staff'

    @classmethod
    def find_by_username(cls, login_id):
        """Find a user by their login ID with role information."""
        session = Session()
        try:
            # Use joined load to fetch role information in the same query
            user = session.query(cls).options(joinedload(cls.role)).filter(cls.login_id == login_id).first()
            return user
        except Exception as e:
            print(f"Error finding user: {e}")
            return None
        finally:
            session.close()
