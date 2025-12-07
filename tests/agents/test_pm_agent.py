import unittest
from unittest.mock import MagicMock, patch, ANY
from agents.pm_agent import PMAgent
from infrastructure.event_bus import EventBus
from infrastructure.llm.reasoning_model_client import ReasoningModelClient
from infrastructure.llm.deep_research_client import DeepResearchClient

class TestPMAgent(unittest.TestCase):
    def setUp(self):
        self.mock_bus = MagicMock(spec=EventBus)
        # Mock DB Client within BaseAgent to avoid real connection attempts if BaseAgent inits it
        with patch('core.base_agent.DBClient') as MockDB:
            self.mock_db_instance = MockDB.return_value
            self.agent = PMAgent("TestPM", self.mock_bus)

        # Mock the specialized clients
        self.agent.reasoning_client = MagicMock(spec=ReasoningModelClient)
        self.agent.deep_research_client = MagicMock(spec=DeepResearchClient)
        
        # Mock the DB client (attached to self.agent.db because of BaseAgent)
        self.agent.db = MagicMock()

    def test_role_property(self):
        self.assertIn("Product Manager", self.agent.role)

    def test_on_segment_request_stale_data(self):
        # Setup: Data is stale (not found in DB)
        self.agent.db.fetch_one.return_value = None
        
        # Setup specific return values for LLM clients
        self.agent.deep_research_client.generate.return_value = "Deep research content..."
        self.agent.reasoning_client.generate.return_value = "Hypothesis content..."

        payload = {"segment_name": "Teens"}
        self.agent.on_segment_request(payload)

        # Verify Deep Research was called
        self.agent.deep_research_client.generate.assert_called_once()
        args, _ = self.agent.deep_research_client.generate.call_args
        self.assertIn("Teens", args[0])

        # Verify Hypothesis Generation was called
        self.agent.reasoning_client.generate.assert_called_once()
        
        # Verify SPEC_COMPLETED event published
        self.mock_bus.publish.assert_called_with("SPEC_COMPLETED", ANY)
        published_args = self.mock_bus.publish.call_args[0][1]
        self.assertEqual(published_args["spec"]["segment"], "Teens")
        self.assertIn("Hypothesis content", published_args["spec"]["full_analysis"])

    def test_on_segment_request_fresh_data(self):
        # Setup: Data is fresh (found in DB)
        self.agent.db.fetch_one.return_value = {"last_updated": "recent"}
        
        self.agent.reasoning_client.generate.return_value = "Hypothesis content..."

        payload = {"segment_name": "Seniors"}
        self.agent.on_segment_request(payload)

        # Verify Deep Research was NOT called
        self.agent.deep_research_client.generate.assert_not_called()

        # Verify Hypothesis Generation was still called
        self.agent.reasoning_client.generate.assert_called_once()

    def test_handle_instruction_market_research(self):
        instruction = "Do a deep dive about Crypto"
        self.agent.deep_research_client.generate.return_value = "Crypto trends..."
        
        self.agent.handle_instruction(instruction, {})

        # Verify Deep Research called with correct topic
        self.agent.deep_research_client.generate.assert_called_once()
        args, _ = self.agent.deep_research_client.generate.call_args
        self.assertIn("Crypto", args[0])

        # Verify Event Published
        self.mock_bus.publish.assert_called_with("RESEARCH_COMPLETED", ANY)

if __name__ == '__main__':
    unittest.main()
