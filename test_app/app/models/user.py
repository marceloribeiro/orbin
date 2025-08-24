"""
User model for the application.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, UUID, Integer
from sqlalchemy.sql import func
from config.database import Base


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    # Primary key and timestamps (always included)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Custom attributes    name = Column(String(255))    email = Column(String(255))    age = Column(Integer)    
    def __repr__(self):
        return f"<User(id={self.id}, name={getattr(self, 'name', None)})>"
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            'id': str(self.id),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,            'name': self.name,            'email': self.email,            'age': self.age,        }