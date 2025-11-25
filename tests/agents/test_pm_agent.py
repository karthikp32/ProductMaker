import unittest
from unittest.mock import MagicMock
from infrastructure.event_bus import EventBus
from agents.pm_agent import PMAgent

class TestPMAgent(unittest.TestCase):
    def setUp(self):
        self.mock_bus = MagicMock(spec=EventBus)
        self.agent = PMAgent("TestPM", self.mock_bus)

    def test_subscription(self):
        # Verify subscriptions are set up
        self.mock_bus.subscribe.assert_any_call("SYSTEM_START", self.agent.on_system_start)
        self.mock_bus.subscribe.assert_any_call("SEGMENT_ANALYSIS_REQUESTED", self.agent.on_segment_request)

    def test_segment_request_flow(self):
        # Mock payload
        payload = {"segment_name": "Test Segment"}
        
        # Run handler
        self.agent.on_segment_request(payload)
        
        # Verify it publishes a spec
        self.mock_bus.publish.assert_called_with("SPEC_COMPLETED", unittest.mock.ANY)

if __name__ == '__main__':
    unittest.main()
