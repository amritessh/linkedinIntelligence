# backend/api/agents.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from models.base import get_db
from models.user import User
from models.profile import LinkedInProfile
from agents.orchestrator import LinkedIntelligenceOrchestrator
from main import get_current_user

router = APIRouter(prefix="/api/agents", tags=["agents"])

# Initialize orchestrator
orchestrator = LinkedIntelligenceOrchestrator()

@router.post("/analyze-profile")
async def analyze_profile(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze a LinkedIn profile using our agent system"""
    
    profile_url = profile_data.get("profile_url")
    message_type = profile_data.get("message_type", "connection_request")
    
    if not profile_url:
        raise HTTPException(status_code=400, detail="Profile URL is required")
    
    try:
        # Process through agent workflow
        result = await orchestrator.process_profile(
            user_id=str(current_user.id),
            profile_url=profile_url,
            message_type=message_type
        )
        
        # Save results to database
        db_profile = LinkedInProfile(
            user_id=current_user.id,
            linkedin_url=profile_url,
            profile_data=result.get("profile_data", {}),
            ai_insights=result.get("ai_insights", {}),
            engagement_score=result.get("engagement_score", 0.0)
        )
        
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        
        return {
            "status": "success",
            "profile_id": str(db_profile.id),
            "analysis": {
                "profile_data": result.get("profile_data"),
                "ai_insights": result.get("ai_insights"),
                "engagement_score": result.get("engagement_score"),
                "personalized_messages": result.get("personalized_messages"),
                "selected_message": result.get("selected_message")
            },
            "workflow_metadata": result.get("metadata"),
            "errors": result.get("errors", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")

@router.get("/profiles")
async def get_user_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all analyzed profiles for the current user"""
    
    profiles = db.query(LinkedInProfile).filter(
        LinkedInProfile.user_id == current_user.id
    ).all()
    
    return {
        "profiles": [
            {
                "id": str(profile.id),
                "linkedin_url": profile.linkedin_url,
                "engagement_score": profile.engagement_score,
                "last_analyzed": profile.last_analyzed,
                "created_at": profile.created_at
            }
            for profile in profiles
        ]
    }

# Add router to main app
# In main.py, add: app.include_router(agents.router)