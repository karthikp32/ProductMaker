import sys
import os
import shutil

from unittest.mock import MagicMock
# Mock DBClient before importing agent to avoid connection issues
import sys
# We need to make sure core.base_agent imports the mocked DBClient or we patch it there
# Simplest: Import core.base_agent and patch it
import core.base_agent
core.base_agent.DBClient = MagicMock()

from agents.frontend_agent import FrontendAgent
from infrastructure.event_bus import EventBus

def test_frontend_generation():
    # Setup
    industry = "athletes"
    output_dir = f"output/{industry}/frontend"
    
    # Cleanup previous run
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    print("Initializing Agent...")
    bus = EventBus()
    agent = FrontendAgent("frontend", bus)

    print(f"Generating code for {industry}...")
    agent.generate_code_from_designs(industry)

    # Verify
    expected_files = [
        "package.json",
        "tsconfig.json",
        "vite.config.ts",
        "index.html",
        "src/main.tsx",
        "src/App.tsx",
        "src/components/Navbar.tsx",
        "src/components/HeroBanner.tsx",
        "src/components/FeaturesList.tsx",
        "src/LandingPage.tsx",
        "src/Dashboard.tsx"
    ]

    missing = []
    for f in expected_files:
        path = os.path.join(output_dir, f)
        if not os.path.exists(path):
            missing.append(f)
    
    if missing:
        print(f"FAILED: Missing files: {missing}")
        sys.exit(1)
    
    print("SUCCESS: All expected files generated.")
    
    # Check content of a component
    with open(os.path.join(output_dir, "src/components/HeroBanner.tsx"), 'r') as f:
        content = f.read()
        if "React.FC" not in content or "Dynamic sports" not in content:
            print("FAILED: implemented component content seems wrong.")
            print(content)
            sys.exit(1)

    print("Component content verified.")

if __name__ == "__main__":
    test_frontend_generation()
