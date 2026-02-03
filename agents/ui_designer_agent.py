import os
import json
import logging
from typing import Any, Dict
from core.base_agent import BaseAgent
from infrastructure.llm.llm_client import LLMClient
from infrastructure.llm.reasoning_model_client import ReasoningModelClient
from infrastructure.event_bus import EventBus

logger = logging.getLogger(__name__)

class UIDesignerAgent(BaseAgent):
    """
    UI Designer Agent: Translates PM output into design direction and structure.
    """
    def __init__(self, name: str, event_bus: EventBus):
        super().__init__(name, event_bus)
        self.reasoning_client = ReasoningModelClient()
    
    @property
    def role(self) -> str:
        return "Senior Product Designer: Create visual direction and UI structure for MVP dashboards."

    @property
    def functions(self) -> list:
        return []

    def setup_subscriptions(self):
        self.event_bus.subscribe("INDUSTRY_WORKFLOW_COMPLETED", self.on_industry_workflow_completed)

    def on_industry_workflow_completed(self, payload: Any):
        industry = payload.get("industry")
        logger.info(f"UI Designer Agent: Industry workflow completed for '{industry}'. Generating designs...")
        self.generate_designs_for_industry(industry)

    def generate_designs_for_industry(self, industry: str):
        safe_industry = industry.replace(" ", "_").lower()
        product_dir = os.path.join("output", safe_industry, "product")
        
        if not os.path.exists(product_dir):
            logger.error(f"UI Designer Agent: Product directory not found: {product_dir}")
            return

        # Load PM output. We'll look for landscape research or PRDs.
        # For simplicity, we'll read the landscape research as the primary context.
        landscape_file = os.path.join(product_dir, "landscape_research.md")
        if not os.path.exists(landscape_file):
            logger.error(f"UI Designer Agent: Landscape research not found: {landscape_file}")
            return
            
        with open(landscape_file, "r") as f:
            pm_context = f.read()

        design_output = self._generate_design_json(pm_context)
        self._persist_designs(industry, design_output)
        
        self.publish_event("DESIGN_COMPLETED", {
            "industry": industry,
            "design": design_output
        })

    def _generate_design_json(self, pm_context: str) -> Dict[str, Any]:
        system_prompt = """
You are a senior product designer designing MVP dashboards.

Your goal is to:
- Create a cohesive visual direction
- Optimize for clarity and trust
- Design for dashboards and data-heavy layouts

Rules:
- Use established design patterns
- Avoid novelty for its own sake
- Favor simple, professional UI
"""
        user_prompt = f"""
Product Context:
{pm_context}

Deliver:
1. Design direction (colors, typography, tone)
2. Page list with purpose
3. Component breakdown per page
4. UX principles to follow

Respond STRICTLY with a JSON object following this structure:
{{
  "design_direction": {{
    "tone": "...",
    "primary_color": "...",
    "accent_color": "...",
    "typography": "...",
    "style_notes": "..."
  }},
  "pages": [
    {{
      "name": "...",
      "purpose": "...",
      "components": ["...", "..."]
    }}
  ],
  "ux_principles": ["...", "..."]
}}
"""
        response = self.reasoning_client.generate(user_prompt, system_prompt=system_prompt)
        
        # Extract JSON from response (handling potential markdown fences)
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"UI Designer Agent: Failed to parse design JSON: {e}")
            return {"error": "Failed to parse design JSON", "raw_response": response}

    def _persist_designs(self, industry: str, design_output: Dict[str, Any]):
        safe_industry = industry.replace(" ", "_").lower()
        design_dir = os.path.join("output", safe_industry, "designs")
        os.makedirs(design_dir, exist_ok=True)
        
        design_file = os.path.join(design_dir, "ui_design.json")
        with open(design_file, "w") as f:
            json.dump(design_output, f, indent=2)
        
        logger.info(f"UI Designer Agent: Designs persisted to {design_file}")
