# backend/api/profiles.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from models.base import get_db
from models.user import User
from models.profile import LinkedInProfile
from main import get_current_user

router = APIRouter(prefix="/api/profiles", tags=["profiles"])

@router.get("/", response_model=List[dict])
async def get_user_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all analyzed profiles for the current user with pagination"""
    
    profiles = db.query(LinkedInProfile).filter(
        LinkedInProfile.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return [
        {
            "id": str(profile.id),
            "linkedin_url": profile.linkedin_url,
            "engagement_score": profile.engagement_score,
            "last_analyzed": profile.last_analyzed,
            "created_at": profile.created_at,
            "profile_summary": {
                "name": profile.profile_data.get("name", "Unknown"),
                "title": profile.profile_data.get("title", ""),
                "company": profile.profile_data.get("experience", [{}])[0].get("company", "") if profile.profile_data.get("experience") else ""
            }
        }
        for profile in profiles
    ]

@router.get("/{profile_id}")
async def get_profile_details(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific profile"""
    
    profile = db.query(LinkedInProfile).filter(
        LinkedInProfile.id == profile_id,
        LinkedInProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "id": str(profile.id),
        "linkedin_url": profile.linkedin_url,
        "profile_data": profile.profile_data,
        "ai_insights": profile.ai_insights,
        "engagement_score": profile.engagement_score,
        "last_analyzed": profile.last_analyzed,
        "created_at": profile.created_at
    }

@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a profile"""
    
    profile = db.query(LinkedInProfile).filter(
        LinkedInProfile.id == profile_id,
        LinkedInProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db.delete(profile)
    db.commit()
    
    return {"message": "Profile deleted successfully"}