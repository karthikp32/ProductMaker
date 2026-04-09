import logging
import sys
import os

# Ensure we can import from the worktree root
sys.path.append(os.getcwd())

from agents.sales_agent import SalesAgent
from infrastructure.event_bus import EventBus
from unittest.mock import MagicMock

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("SalesVerify")

class MockEventBus:
    def subscribe(self, event, handler):
        logger.info(f"[Bus] Subscribed to {event}")
    
    def publish(self, event, payload):
        logger.info(f"[Bus] Published {event}: {payload}")

def main():
    logger.info("--- Starting Sales Agent Verification ---")
    
    # Mock EventBus
    bus = MockEventBus()
    
    # Initialize Agent
    agent = SalesAgent("SalesAgent", bus)
    
    # Mock LLM to avoid API keys requirement and latency during verify
    # (We are verifying the FLOW, the LLM call is an internal detail, but let's mock the response)
    agent.reasoning_client = MagicMock()
    agent.reasoning_client.generate.return_value = '{"subject": "Meeting?", "body": "Hi there, wanna buy?"}'
    
    # Simulate a lead
    lead_payload = {
        "lead": {
            "name": "Alice Smith",
            "email": "alice@example.com",
            "context": "CEO of TechCorp. Interested in AI agents."
        }
    }
    
    logger.info("Triggering on_lead_generated...")
    agent.on_lead_generated(lead_payload)
    
    logger.info("--- Verification Complete ---")

if __name__ == "__main__":
    main()
