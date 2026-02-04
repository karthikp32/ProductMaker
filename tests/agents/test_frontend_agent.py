import unittest
import os
import shutil
import json
from unittest.mock import MagicMock, patch
from infrastructure.event_bus import EventBus
from agents.frontend_agent import FrontendAgent

class TestFrontendAgent(unittest.TestCase):
    def setUp(self):
        # Mock DBClient
        with patch('core.base_agent.DBClient'):
            self.mock_bus = MagicMock(spec=EventBus)
            self.agent = FrontendAgent("TestFrontend", self.mock_bus)
        
        self.test_industry = "test_frontend_industry"
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        self.output_dir = os.path.join(self.base_dir, "output", self.test_industry)
        self.designs_dir = os.path.join(self.output_dir, "designs")
        self.frontend_dir = os.path.join(self.output_dir, "frontend")

        # Cleanup
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        
        # Create designs directory
        os.makedirs(self.designs_dir)

    def tearDown(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_generate_code_from_designs(self):
        # Create a mock design
        design_content = {
            "direction": "Modern",
            "pages": [
                {
                    "name": "TestPage",
                    "components": [
                        {"name": "TestComponent", "description": "A test component"}
                    ]
                }
            ]
        }
        with open(os.path.join(self.designs_dir, "design.json"), "w") as f:
            json.dump(design_content, f)

        # Run generation
        # We need to ensure the agent uses the absolute path relative to where we are running
        # The agent uses output/{industry}/... relative to CWD.
        # So we should chdir to project root or patch paths.
        # But agent implementation uses absolute paths? Let's check agent implementation again.
        # It uses: os.path.abspath(f"output/{industry}/designs")
        # So if we run this test from project root, it works.
        # Ideally we should mock os.path.abspath or chdir.
        
        cwd = os.getcwd()
        try:
            os.chdir(self.base_dir)
            self.agent.generate_code_from_designs(self.test_industry)
        finally:
            os.chdir(cwd)

        # Verify output
        self.assertTrue(os.path.exists(os.path.join(self.frontend_dir, "package.json")))
        self.assertTrue(os.path.exists(os.path.join(self.frontend_dir, "src/TestPage.tsx")))
        self.assertTrue(os.path.exists(os.path.join(self.frontend_dir, "src/components/TestComponent.tsx")))

        # Check content
        with open(os.path.join(self.frontend_dir, "src/components/TestComponent.tsx"), "r") as f:
            content = f.read()
            self.assertIn("React.FC", content)
            self.assertIn("A test component", content)

if __name__ == '__main__':
    unittest.main()
