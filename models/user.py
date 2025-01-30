from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from utils.database import Session
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(100), unique=True, nullable=False)
    avatar = Column(String(100), unique=False, nullable=True)
    password = Column(String(255), nullable=False)
    ptext = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    # role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    # role = relationship("Role", back_populates="users")
    # shops = relationship("Shop", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    @classmethod
    def find_by_username(cls, username):
        """Find a user by their username."""
        session = Session()
        try:
            user = session.query(cls).filter(cls.username == username).first()
            return user
        finally:
            session.close()
