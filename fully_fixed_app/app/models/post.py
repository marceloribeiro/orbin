"""
Post model for the application.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, UUID, Text
from sqlalchemy.sql import func
from config.database import Base


class Post(Base):
    """Post model."""
    
    __tablename__ = "posts"
    
    # Primary key and timestamps (always included)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Custom attributes    title = Column(String(255))    content = Column(Text)    user_id = Column(UUID(as_uuid=True))    
    def __repr__(self):
        return f"<Post(id={self.id}, title={getattr(self, 'title', None)})>"
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            'id': str(self.id),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,            'title': self.title,            'content': self.content,            'user_id': self.user_id,        }