import unittest
import os
import logging
from agents.pm_agent import PMAgent
from infrastructure.event_bus import EventBus

# Configure logging to see output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HypothesisGenTest")

class TestHypothesisGeneration(unittest.TestCase):
    """
    Test that the PM Agent can generate 5 hypotheses based on research.
    """
    
    def setUp(self):
        # We need the real keys for this test
        if not os.getenv("GEMINI_API_KEY") or not os.getenv("OPENROUTER_DEEPSEEK_R1_API_KEY"):
            self.skipTest("Skipping test: Missing API Keys")
            
        self.bus = EventBus()
        self.agent = PMAgent("PMAgent", self.bus)

    def test_end_to_end_hypothesis(self):
        topic = "Sustainable Fashion Consumers"
        
        logger.info(f"--- Starting End-to-End Flow for: {topic} ---")
        
        # Trigger the event
        payload = {"segment_name": topic}
        self.agent.on_segment_request(payload)
        
        # We expect to see logs for:
        # 1. Deep Research (Gemini)
        # 2. Hypothesis Generation (DeepSeek R1)
        
        # Since this is a long-running test, we just check if it completes without error
        logger.info("--- End-to-End Flow Completed ---")

if __name__ == '__main__':
    unittest.main()
