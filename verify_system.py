import logging
import time
from infrastructure.event_bus import EventBus
from core.orchestrator import Orchestrator
from agents.pm_agent import PMAgent
from agents.designer_agent import DesignerAgent
from agents.architect_agent import ArchitectAgent
from agents.frontend_agent import FrontendAgent
from agents.backend_agent import BackendAgent
from agents.marketing_agent import MarketingAgent
from agents.sales_agent import SalesAgent
from agents.analytics_agent import AnalyticsAgent

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    # 1. Setup Infrastructure
    bus = EventBus()
    
    # 2. Initialize Core
    orchestrator = Orchestrator(bus)
    
    # 3. Initialize Agents
    pm = PMAgent("PM", bus)
    designer = DesignerAgent("Designer", bus)
    architect = ArchitectAgent("Architect", bus)
    frontend = FrontendAgent("Frontend", bus)
    backend = BackendAgent("Backend", bus)
    marketing = MarketingAgent("Marketing", bus)
    sales = SalesAgent("Sales", bus)
    analytics = AnalyticsAgent("Analytics", bus)
    
    # 4. Start System
    orchestrator.start()
    
    # 5. Simulate User Request
    bus.publish("SEGMENT_ANALYSIS_REQUESTED", {"segment_name": "Indie Game Developers"})
    
    # 6. Wait for async events (simulated)
    time.sleep(2)

if __name__ == "__main__":
    main()
