import unittest
from unittest.mock import MagicMock, ANY, patch
from infrastructure.event_bus import EventBus
from agents.sales_agent import SalesAgent

class TestSalesAgent(unittest.TestCase):
    @patch('core.base_agent.LLMClient')
    @patch('core.base_agent.DBClient')
    def setUp(self, mock_db, mock_llm):
        self.mock_bus = MagicMock(spec=EventBus)
        self.agent = SalesAgent("TestSales", self.mock_bus)

    def test_subscription(self):
        # Verify subscriptions are set up
        self.mock_bus.subscribe.assert_called_with("LEAD_GENERATED", self.agent.on_lead_generated)

    def test_lead_generated_flow(self):
        # Mock payload
        payload = {"lead": "Test Lead"}
        
        # Run handler
        self.agent.on_lead_generated(payload)
        
        # Verify it publishes outreach sent
        self.mock_bus.publish.assert_called_with("OUTREACH_SENT", ANY)
        
        # Verify the content of the published event if possible, or just that it was called
        # We can inspect the call args to be more specific
        args, _ = self.mock_bus.publish.call_args
        self.assertEqual(args[0], "OUTREACH_SENT")
        self.assertIn("email", args[1])
        self.assertEqual(args[1]["email"], "Hey, saw you were interested...")

if __name__ == '__main__':
    unittest.main()
