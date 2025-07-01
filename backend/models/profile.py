# backend/models/profile.py
from sqlalchemy import Column, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class LinkedInProfile(Base):
    __tablename__ = "linkedin_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    linkedin_url = Column(String, nullable=False)
    profile_data = Column(JSON, default=dict)
    ai_insights = Column(JSON, default=dict)
    engagement_score = Column(Float, default=0.0)
    last_analyzed = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profiles")