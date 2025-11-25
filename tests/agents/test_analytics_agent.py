import unittest
from unittest.mock import MagicMock, ANY
from infrastructure.event_bus import EventBus
from agents.analytics_agent import AnalyticsAgent

class TestAnalyticsAgent(unittest.TestCase):
    def setUp(self):
        self.mock_bus = MagicMock(spec=EventBus)
        self.agent = AnalyticsAgent("TestAnalytics", self.mock_bus)

    def test_subscription(self):
        # Verify subscriptions are set up
        self.mock_bus.subscribe.assert_any_call("EXPERIMENT_ENDED", self.agent.on_experiment_ended)

    def test_experiment_ended_flow(self):
        # Mock payload
        payload = {"experiment_id": "exp_123"}
        
        # Run handler
        self.agent.on_experiment_ended(payload)
        
        # Verify it publishes a report
        # The agent currently hardcodes the return value of _calculate_stats
        expected_report = {"roi": 1.5, "verdict": "SCALE"}
        self.mock_bus.publish.assert_called_with("REPORT_GENERATED", {"report": expected_report})

if __name__ == '__main__':
    unittest.main()
