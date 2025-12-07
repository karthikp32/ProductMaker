import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

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

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ProductMaker API")

# Initialize System
event_bus = EventBus()
orchestrator = Orchestrator(event_bus)

# Initialize Agents
agents = {
    "pm": PMAgent("pm", event_bus),
    "designer": DesignerAgent("designer", event_bus),
    "architect": ArchitectAgent("architect", event_bus),
    "frontend": FrontendAgent("frontend", event_bus),
    "backend": BackendAgent("backend", event_bus),
    "marketing": MarketingAgent("marketing", event_bus),
    "sales": SalesAgent("sales", event_bus),
    "analytics": AnalyticsAgent("analytics", event_bus),
}

# Start Orchestrator
orchestrator.start()

class InstructionRequest(BaseModel):
    instruction: str
    context: Optional[Dict[str, Any]] = {}

@app.post("/instruct/{agent_name}")
async def instruct_agent(agent_name: str, request: InstructionRequest):
    agent_name = agent_name.lower()
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found.")
    
    event_type = f"INSTRUCT_{agent_name.upper()}"
    payload = {
        "instruction": request.instruction,
        "context": request.context
    }
    
    logger.info(f"API: Instructing {agent_name} with: {request.instruction}")
    event_bus.publish(event_type, payload)
    
    return {"status": "Instruction sent", "agent": agent_name}

@app.get("/agents")
async def list_agents():
    return {"agents": list(agents.keys())}
