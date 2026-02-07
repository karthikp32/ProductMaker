import unittest
from unittest.mock import MagicMock, patch, ANY
import os
from agents.architect_agent import ArchitectAgent
from infrastructure.event_bus import EventBus
from infrastructure.llm.reasoning_model_client import ReasoningModelClient

class TestArchitectAgent(unittest.TestCase):
    @patch('agents.architect_agent.ReasoningModelClient')
    def setUp(self, MockReasoningClient):
        self.mock_bus = MagicMock(spec=EventBus)
        # Mock DB Client within BaseAgent
        with patch('core.base_agent.DBClient') as MockDB:
            # Instantiate the agent. The MockReasoningClient will be used inside __init__
            self.agent = ArchitectAgent("TestArchitect", self.mock_bus)
        
        # Access the mock that was used
        self.mock_reasoning_client = self.agent.reasoning_client
        self.mock_reasoning_client.generate.return_value = "# System Architecture\nDetails..."

    def test_role_property(self):
        self.assertIn("Software Architect", self.agent.role)

    @patch('subprocess.run')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_on_prd_completed(self, mock_open, mock_makedirs, mock_git):
        payload = {
            "prd_content": "Build a movie crowdfunding platform.",
            "project_name": "MovieMaker"
        }
        
        # Trigger the event handler
        self.agent.on_prd_completed(payload)
        
        # Verify LLM was called
        self.mock_reasoning_client.generate.assert_called()
        
        # Verify file was written
        mock_open.assert_called()
        
        # Verify Git commit was attempted
        mock_git.assert_called()
        
        # Verify event was published
        self.mock_bus.publish.assert_called_with("DESIGN_DOC_COMPLETED", ANY)

    def test_handle_instruction_design(self):
        instruction = "Design the architecture for this PRD"
        context = {
            "prd_content": "A simple todo app.",
            "project_name": "TodoApp"
        }
        
        with patch.object(self.agent, '_run_design_workflow') as mock_workflow:
            self.agent.handle_instruction(instruction, context)
            mock_workflow.assert_called_once_with("A simple todo app.", "TodoApp")

if __name__ == '__main__':
    unittest.main()
