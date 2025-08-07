from sqlalchemy import Column, Integer, String, Date, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import os

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Підтримка як PostgreSQL, так і SQLite
    if os.getenv("DATABASE_URL", "").startswith("postgresql"):
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    else:
        # SQLite не підтримує timezone
        created_at = Column(DateTime, server_default=func.now())
        updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationship with contacts
    contacts = relationship("Contact", back_populates="user", cascade="all, delete-orphan")

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    birth_date = Column(Date, nullable=False)
    additional_data = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationship with user
    user = relationship("User", back_populates="contacts")
    
    # Підтримка як PostgreSQL, так і SQLite
    if os.getenv("DATABASE_URL", "").startswith("postgresql"):
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    else:
        # SQLite не підтримує timezone
        created_at = Column(DateTime, server_default=func.now())
        updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())