import unittest
import os
import shutil
import json
from unittest.mock import MagicMock, patch, ANY
from infrastructure.event_bus import EventBus
from agents.ui_designer_agent import UIDesignerAgent

class TestUIDesignerAgent(unittest.TestCase):
    def setUp(self):
        self.mock_bus = MagicMock(spec=EventBus)
        # Mock ReasoningModelClient to avoid actual LLM calls
        with patch('agents.ui_designer_agent.ReasoningModelClient') as MockReasoning:
            self.mock_reasoning_client = MockReasoning.return_value
            self.agent = UIDesignerAgent("TestUIDesigner", self.mock_bus)
            # Reassign the mocked client to the agent instance
            self.agent.reasoning_client = self.mock_reasoning_client

        # Setup paths
        self.industry = "test_athletes"
        self.safe_industry = self.industry.replace(" ", "_").lower()
        self.product_dir = os.path.join("output", self.safe_industry, "product")
        self.designs_dir = os.path.join("output", self.safe_industry, "designs")
        
        # Cleanup before test
        if os.path.exists(f"output/{self.safe_industry}"):
            shutil.rmtree(f"output/{self.safe_industry}")
            
        os.makedirs(self.product_dir, exist_ok=True)

    def tearDown(self):
        # Cleanup after test
        if os.path.exists(f"output/{self.safe_industry}"):
            shutil.rmtree(f"output/{self.safe_industry}")

    def test_subscription(self):
        self.mock_bus.subscribe.assert_called_with("INDUSTRY_WORKFLOW_COMPLETED", self.agent.on_industry_workflow_completed)

    def test_generate_designs_flow(self):
        # 1. Setup Input Data (Mock PM Output)
        landscape_file = os.path.join(self.product_dir, "landscape_research.md")
        with open(landscape_file, "w") as f:
            f.write("# Market Research\nContext for testing.")
            
        # 2. Mock LLM Response
        mock_design_json = {
            "design_direction": {
                "tone": "Test Tone",
                "primary_color": "Blue"
            },
            "pages": [],
            "ux_principles": []
        }
        self.mock_reasoning_client.generate.return_value = json.dumps(mock_design_json)

        # 3. Trigger Action
        self.agent.generate_designs_for_industry(self.industry)

        # 4. Verify Output File Exists
        design_file = os.path.join(self.designs_dir, "ui_design.json")
        self.assertTrue(os.path.exists(design_file), "Design JSON file should be created")
        
        with open(design_file, "r") as f:
            data = json.load(f)
            self.assertEqual(data["design_direction"]["tone"], "Test Tone")

        # 5. Verify Event Published
        self.mock_bus.publish.assert_called_with("DESIGN_COMPLETED", ANY)
        args, _ = self.mock_bus.publish.call_args
        self.assertEqual(args[1]["industry"], self.industry)

if __name__ == '__main__':
    unittest.main()
