# backend/agents/orchestrator.py
from langgraph.graph import StateGraph, END
from .base import LinkedIntelligenceState
from .profile_intelligence import ProfileIntelligenceAgent
from .personalization import PersonalizationAgent

class LinkedIntelligenceOrchestrator:
    """Main orchestrator for the multi-agent workflow"""
    
    def __init__(self):
        self.profile_agent = ProfileIntelligenceAgent()
        self.personalization_agent = PersonalizationAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the agent workflow graph"""
        
        # Create the state graph
        workflow = StateGraph(LinkedIntelligenceState)
        
        # Add agent nodes
        workflow.add_node("profile_analysis", self.profile_agent.execute)
        workflow.add_node("personalization", self.personalization_agent.execute)
        workflow.add_node("error_handler", self._handle_errors)
        
        # Define the workflow
        workflow.set_entry_point("profile_analysis")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "profile_analysis",
            self._route_after_profile_analysis,
            {
                "personalization": "personalization",
                "error": "error_handler",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "personalization",
            self._route_after_personalization,
            {
                "end": END,
                "error": "error_handler"
            }
        )
        
        workflow.add_edge("error_handler", END)
        
        return workflow.compile()
    
    def _route_after_profile_analysis(self, state: LinkedIntelligenceState) -> str:
        """Decide next step after profile analysis"""
        if state.get("errors"):
            return "error"
        
        if state.get("next_action") == "generate_messages":
            return "personalization"
        
        return "end"
    
    def _route_after_personalization(self, state: LinkedIntelligenceState) -> str:
        """Decide next step after personalization"""
        if state.get("errors"):
            return "error"
        
        return "end"
    
    def _handle_errors(self, state: LinkedIntelligenceState) -> LinkedIntelligenceState:
        """Handle errors in the workflow"""
        errors = state.get("errors", [])
        print(f"Workflow errors: {errors}")
        
        state.update({
            "current_step": "error_handled",
            "next_action": "end"
        })
        
        return state
    
    async def process_profile(
        self, 
        user_id: str, 
        profile_url: str, 
        message_type: str = "connection_request"
    ) -> LinkedIntelligenceState:
        """Process a LinkedIn profile through the agent workflow"""
        
        # Initialize state
        initial_state = LinkedIntelligenceState(
            user_id=user_id,
            profile_url=profile_url,
            message_type=message_type,
            profile_data=None,
            ai_insights=None,
            engagement_score=None,
            message_templates=None,
            personalized_messages=None,
            selected_message=None,
            current_step="initialized",
            next_action="analyze_profile",
            errors=[],
            metadata={"workflow_id": f"workflow_{user_id}_{hash(profile_url)}"}
        )
        
        # Execute the workflow
        result = self.graph.invoke(initial_state)
        
        return result