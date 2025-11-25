from typing import Any
import logging
from core.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class FrontendAgent(BaseAgent):
    """
    Frontend SWE Agent: Owns the 'Interaction'.
    """
    def setup_subscriptions(self):
        self.event_bus.subscribe("ARCHITECTURE_APPROVED", self.on_architecture_approved)

    def on_architecture_approved(self, payload: Any):
        logger.info("Frontend Agent: Architecture ready. Building UI components...")
        
        # 1. Write Code
        self._write_react_code()
        
        # 2. Publish
        self.publish_event("FRONTEND_BUILT", {"status": "success"})

    def _write_react_code(self):
        # TODO: Call LLM to write React components
        logger.info("Frontend Agent: [Tool Call] Writing React Code...")
