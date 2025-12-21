from typing import Any
import logging
from core.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class SalesAgent(BaseAgent):
    """
    Sales Agent: Owns 'Conversion'.
    """
    @property
    def role(self) -> str:
        return "Sales Representative: Lead engagement and conversion."

    @property
    def functions(self) -> list:
        return []
    def setup_subscriptions(self):
        self.event_bus.subscribe("LEAD_GENERATED", self.on_lead_generated)

    def on_lead_generated(self, payload: Any):
        lead = payload.get("lead")
        logger.info(f"Sales Agent: New lead '{lead}'. Drafting outreach...")
        
        # 1. Draft Email
        email = self._draft_email(lead)
        
        # 2. Publish
        self.publish_event("OUTREACH_SENT", {"email": email})

    def _draft_email(self, lead: str) -> str:
        # TODO: Call LLM
        logger.info("Sales Agent: [Tool Call] Drafting Cold Email...")
        return "Hey, saw you were interested..."
