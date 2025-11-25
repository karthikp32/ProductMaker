from typing import Any
import logging
from core.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class PMAgent(BaseAgent):
    """
    Product Manager Agent: Owns the 'Why' and 'What'.
    """
    def setup_subscriptions(self):
        self.event_bus.subscribe("SYSTEM_START", self.on_system_start)
        self.event_bus.subscribe("SEGMENT_ANALYSIS_REQUESTED", self.on_segment_request)

    def on_system_start(self, payload: Any):
        logger.info("PM Agent online. Waiting for instructions.")

    def on_segment_request(self, payload: Any):
        segment_name = payload.get("segment_name")
        logger.info(f"PM Agent: Analyzing segment '{segment_name}'...")
        
        # 1. Check Freshness (Mock Logic)
        is_fresh = self._check_data_freshness(segment_name)
        
        if not is_fresh:
            logger.info("PM Agent: Data stale. Initiating Deep Research...")
            self._run_deep_research(segment_name)
        else:
            logger.info("PM Agent: Data fresh. Skipping research.")

        # 2. Generate Hypothesis
        hypothesis = self._generate_hypothesis(segment_name)
        
        # 3. Publish Spec
        self.publish_event("SPEC_COMPLETED", {"spec": hypothesis})

    def _check_data_freshness(self, segment_name: str) -> bool:
        # TODO: Query DB for last_updated timestamp
        return False # Force research for V0

    def _run_deep_research(self, segment_name: str):
        # TODO: Call Perplexity/Google Search API
        logger.info(f"PM Agent: [Tool Call] Deep Researching {segment_name}...")

    def _generate_hypothesis(self, segment_name: str) -> dict:
        # TODO: Call LLM
        return {
            "segment": segment_name,
            "hypothesis": "If we build X, they will buy Y.",
            "features": ["Feature A", "Feature B"]
        }
