# tests/test_agents.py
import pytest
from backend.agents.orchestrator import LinkedIntelligenceOrchestrator
from backend.agents.base import LinkedIntelligenceState

@pytest.mark.asyncio
async def test_profile_analysis_workflow():
    """Test the complete agent workflow"""
    
    orchestrator = LinkedIntelligenceOrchestrator()
    
    # Test data
    result = await orchestrator.process_profile(
        user_id="test-user-123",
        profile_url="https://linkedin.com/in/test-profile",
        message_type="connection_request"
    )
    
    # Assertions
    assert result["current_step"] is not None
    assert result["profile_data"] is not None
    assert result["ai_insights"] is not None
    assert result["engagement_score"] >= 0.0
    assert result["personalized_messages"] is not None
    assert len(result["personalized_messages"]) > 0
    assert result["selected_message"] is not None

@pytest.mark.asyncio
async def test_profile_intelligence_agent():
    """Test profile intelligence agent individually"""
    
    from backend.agents.profile_intelligence import ProfileIntelligenceAgent
    
    agent = ProfileIntelligenceAgent()
    
    initial_state = LinkedIntelligenceState(
        user_id="test-user",
        profile_url="https://linkedin.com/in/test",
        message_type="connection_request",
        profile_data=None,
        ai_insights=None,
        engagement_score=None,
        message_templates=None,
        personalized_messages=None,
        selected_message=None,
        current_step="initialized",
        next_action="analyze_profile",
        errors=[],
        metadata={}
    )
    
    result = agent.execute(initial_state)
    
    assert result["profile_data"] is not None
    assert result["ai_insights"] is not None
    assert result["engagement_score"] > 0

# Run tests with: pytest tests/ -v