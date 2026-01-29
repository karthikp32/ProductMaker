import sys
import os
import json
import logging
import unittest
from unittest.mock import MagicMock

# Add the worktree to sys.path first to prioritize it
worktree_path = os.path.join(os.getcwd(), "sales_agent_worktree")
sys.path.insert(0, worktree_path)

from agents.sales_agent import SalesAgent
from infrastructure.event_bus import EventBus
from infrastructure.db.db_client import DBClient

# Configure logging to see the output
logging.basicConfig(level=logging.INFO)

class TestSalesAgentHandoff(unittest.TestCase):
    def setUp(self):
        # Mock DBClient to avoid connection errors during initialization
        with unittest.mock.patch('infrastructure.db.db_client.DBClient'):
            self.mock_event_bus = MagicMock(spec=EventBus)
            self.agent = SalesAgent(name="SalesAgent", event_bus=self.mock_event_bus)
        
        # Mock the LLM client
        self.agent.reasoning_client = MagicMock()
        self.agent.reasoning_client.generate.return_value = json.dumps({
            "analysis": {"fit": "high", "urgency": "high", "notes": "Looks good"},
            "actions": [{"type": "send_email", "payload": {"subject": "Hi", "body": "Welcome"}}],
            "sales_outcome": {"status": "in_progress", "notes": "Contacted"}
        })

    def test_on_marketing_lead_handoff(self):
        """
        Tests that the Sales Agent processes a MARKETING_LEAD_HANDOFF event.
        """
        payload = {
            "handoff": {
                "from": "MarketingAgent",
                "to": "SalesAgent",
                "lead_id": "lead_123",
                "lead_score": 85,
                "context": "Lead showed high interest in the pricing page.",
                "product_context": {
                    "product_name": "ProductMaker",
                    "pricing_assumption": "$99/mo",
                    "target_persona": "Indie Founders"
                },
                "lead": {
                    "lead_id": "lead_123",
                    "email": "test@example.com",
                    "lead_score": 85,
                    "engagement_summary": "Visited pricing 3 times.",
                    "qualification_notes": []
                }
            }
        }

        # Trigger the handoff
        self.agent.on_marketing_lead_handoff(payload)

        # Verify that an event was published back to the bus
        self.assertTrue(self.mock_event_bus.publish.called)
        
        # Check the published event type
        args, kwargs = self.mock_event_bus.publish.call_args_list[-1]
        event_type = args[0]
        event_payload = args[1]
        
        self.assertEqual(event_type, "SALES_QUALIFICATION_COMPLETED")
        self.assertEqual(event_payload["lead_id"], "lead_123")
        self.assertIn("outcome", event_payload)
        self.assertIn("status", event_payload["outcome"])

if __name__ == "__main__":
    unittest.main()
