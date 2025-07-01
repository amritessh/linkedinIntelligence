# backend/agents/base.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional, Any
from pydantic import BaseModel
import uuid
from datetime import datetime

# Global state for our multi-agent system
class LinkedIntelligenceState(TypedDict):
    # Input data
    user_id: str
    profile_url: str
    message_type: str
    
    # Profile analysis
    profile_data: Optional[dict]
    ai_insights: Optional[dict]
    engagement_score: Optional[float]
    
    # Message generation
    message_templates: Optional[List[str]]
    personalized_messages: Optional[List[dict]]
    selected_message: Optional[dict]
    
    # Workflow control
    current_step: str
    next_action: str
    errors: List[str]
    metadata: dict

class BaseAgent:
    """Base class for all agents in the system"""
    
    def __init__(self, name: str):
        self.name = name
        self.execution_count = 0
    
    def execute(self, state: LinkedIntelligenceState) -> LinkedIntelligenceState:
        """Execute the agent's main logic"""
        self.execution_count += 1
        print(f"Executing {self.name} (run #{self.execution_count})")
        
        try:
            return self._execute_logic(state)
        except Exception as e:
            state["errors"].append(f"{self.name}: {str(e)}")
            return state
    
    def _execute_logic(self, state: LinkedIntelligenceState) -> LinkedIntelligenceState:
        """Override this method in subclasses"""
        raise NotImplementedError