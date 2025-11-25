from typing import Any
import logging
from core.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class MarketingAgent(BaseAgent):
    """
    Marketing Agent: Owns 'Awareness'.
    """
    def setup_subscriptions(self):
        self.event_bus.subscribe("MVP_DEPLOYED", self.on_mvp_deployed)

    def on_mvp_deployed(self, payload: Any):
        logger.info("Marketing Agent: MVP is live! Generating campaigns...")
        
        # 1. Generate Copy
        campaigns = self._generate_campaigns()
        
        # 2. Publish
        self.publish_event("CAMPAIGN_LAUNCHED", {"campaigns": campaigns})

    def _generate_campaigns(self) -> dict:
        # TODO: Call LLM
        logger.info("Marketing Agent: [Tool Call] Writing Ad Copy...")
        return {"twitter": "Check out this new tool!", "reddit": "I built this for you..."}
