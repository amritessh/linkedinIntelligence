# backend/agents/personalization.py
from .base import BaseAgent, LinkedIntelligenceState
from typing import List, Dict, Any

class PersonalizationAgent(BaseAgent):
    """Agent responsible for generating personalized messages"""
    
    def __init__(self):
        super().__init__("PersonalizationAgent")
        self.message_templates = {
            "connection_request": [
                "Hi {name}, I noticed your work at {company} and would love to connect!",
                "Hello {name}, fellow {industry} professional here. Let's connect!",
                "Hi {name}, I saw your recent post about {topic} and found it insightful."
            ],
            "follow_up": [
                "Thanks for connecting, {name}! I'd love to learn more about {company_initiative}.",
                "Hi {name}, hope you're doing well at {company}. Any thoughts on {industry_trend}?"
            ]
        }
    
    def _execute_logic(self, state: LinkedIntelligenceState) -> LinkedIntelligenceState:
        profile_data = state.get("profile_data")
        ai_insights = state.get("ai_insights")
        message_type = state.get("message_type", "connection_request")
        
        if not profile_data or not ai_insights:
            state["errors"].append("Missing profile data or insights")
            return state
        
        # Generate personalized messages
        personalized_messages = self._generate_personalized_messages(
            profile_data, ai_insights, message_type
        )
        
        # Select best message
        selected_message = self._select_best_message(personalized_messages, ai_insights)
        
        # Update state
        state.update({
            "message_templates": self.message_templates.get(message_type, []),
            "personalized_messages": personalized_messages,
            "selected_message": selected_message,
            "current_step": "personalization_complete",
            "next_action": "ready_for_sending"
        })
        
        return state
    
    def _generate_personalized_messages(
        self, 
        profile_data: Dict[str, Any], 
        ai_insights: Dict[str, Any], 
        message_type: str
    ) -> List[Dict[str, Any]]:
        """Generate multiple personalized message variants"""
        
        templates = self.message_templates.get(message_type, [])
        personalized = []
        
        for i, template in enumerate(templates):
            # Extract personalization data
            name = profile_data.get("name", "").split()[0]  # First name
            company = self._extract_company(profile_data)
            industry = self._extract_industry(profile_data)
            topic = self._extract_recent_topic(profile_data)
            
            # Personalize the template
            personalized_message = template.format(
                name=name,
                company=company,
                industry=industry,
                topic=topic,
                company_initiative="your latest product launch"  # TODO: Extract from news
            )
            
            personalized.append({
                "id": i,
                "template_id": i,
                "content": personalized_message,
                "tone": ai_insights.get("message_tone", "professional"),
                "confidence_score": 0.8,  # TODO: Calculate based on personalization quality
                "personalization_elements": {
                    "name": name,
                    "company": company,
                    "topic": topic
                }
            })
        
        return personalized
    
    def _select_best_message(
        self, 
        messages: List[Dict[str, Any]], 
        ai_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Select the best message based on AI insights"""
        if not messages:
            return {}
        
        # For now, select highest confidence score
        # TODO: Implement ML-based selection
        return max(messages, key=lambda x: x.get("confidence_score", 0))
    
    def _extract_company(self, profile_data: Dict[str, Any]) -> str:
        """Extract current company from profile"""
        experience = profile_data.get("experience", [])
        if experience:
            return experience[0].get("company", "your company")
        return "your company"
    
    def _extract_industry(self, profile_data: Dict[str, Any]) -> str:
        """Extract industry from profile"""
        title = profile_data.get("title", "")
        if "engineer" in title.lower():
            return "tech"
        return "professional"
    
    def _extract_recent_topic(self, profile_data: Dict[str, Any]) -> str:
        """Extract recent topic from posts"""
        recent_posts = profile_data.get("recent_posts", [])
        if recent_posts:
            content = recent_posts[0].get("content", "")
            if "AI" in content:
                return "AI developments"
        return "industry trends"