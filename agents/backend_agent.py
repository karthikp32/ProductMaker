from typing import Any
import logging
from core.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class BackendAgent(BaseAgent):
    """
    Backend SWE Agent: Owns the 'Logic'.
    """
    def setup_subscriptions(self):
        self.event_bus.subscribe("ARCHITECTURE_APPROVED", self.on_architecture_approved)

    def on_architecture_approved(self, payload: Any):
        logger.info("Backend Agent: Architecture ready. Building API handlers...")
        
        # 1. Write Code
        self._write_api_handlers()
        
        # 2. Publish
        self.publish_event("BACKEND_BUILT", {"status": "success"})

    def _write_api_handlers(self):
        # TODO: Call LLM to write Python/FastAPI code
        logger.info("Backend Agent: [Tool Call] Writing API Handlers...")
