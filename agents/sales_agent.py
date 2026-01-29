import logging
import os
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from core.base_agent import BaseAgent, AgentFunction
from agents.interfaces.sales_agent_interface import SalesAgentInterface
from infrastructure.llm.reasoning_model_client import ReasoningModelClient
from agents.prompts.sales_prompts import get_sdr_system_prompt, get_qualification_prompt

logger = logging.getLogger(__name__)

class SalesAgent(SalesAgentInterface):
    """
    Sales Agent: Owns 'Conversion' and lead qualification.
    """
    def __init__(self, name: str, event_bus: Any):
        super().__init__(name, event_bus)
        self.reasoning_client = ReasoningModelClient()

    @property
    def role(self) -> str:
        return "AI Sales Development Representative: Qualifying high-intent leads and driving conversions."

    @property
    def functions(self) -> List[AgentFunction]:
        return []

    def setup_subscriptions(self):
        # Listen for handoffs from Marketing
        self.event_bus.subscribe("MARKETING_LEAD_HANDOFF", self.on_marketing_lead_handoff)
        # Compatibility support for generic lead events
        self.event_bus.subscribe("LEAD_GENERATED", self.on_lead_generated)

    def on_marketing_lead_handoff(self, payload: Any):
        """
        Main entry point for Sales Agent. Receives a qualified lead from Marketing.
        """
        handoff_data = payload.get("handoff", {})
        lead_id = handoff_data.get("lead_id")
        logger.info(f"Sales Agent: Received handoff for lead {lead_id}")

        # 1. Qualify the lead using LLM
        qualification_report = self.qualify_lead(handoff_data)
        
        # 2. Execute recommended actions
        actions = qualification_report.get("actions", [])
        for action in actions:
            self.execute_sales_action(action.get("type"), action.get("payload", {}))

        # 3. Log results
        outcome = qualification_report.get("sales_outcome", {})
        self.publish_event("SALES_QUALIFICATION_COMPLETED", {
            "lead_id": lead_id,
            "outcome": outcome,
            "report": qualification_report
        })

    def on_lead_generated(self, payload: Any):
        """
        Legacy/Generic lead handler. Wraps it into a handoff-like structure for qualification.
        """
        lead = payload.get("lead", {})
        if isinstance(lead, str):
            lead = {"name": "Prospect", "context": lead}
        
        mock_handoff = {
            "lead": lead,
            "product_context": {"product_name": "ProductMaker", "pricing_assumption": "SaaS Subscription"},
            "context": "Direct lead generation"
        }
        self.on_marketing_lead_handoff({"handoff": mock_handoff})

    def qualify_lead(self, handoff_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calls the LLM to analyze the lead and determine the next steps.
        """
        product_context = handoff_data.get("product_context", {})
        lead_context = handoff_data.get("lead", {})
        
        system_prompt = get_sdr_system_prompt()
        prompt = get_qualification_prompt(product_context, lead_context)
        
        logger.info(f"Sales Agent: Qualifying lead...")
        response = self.reasoning_client.generate(prompt, system_prompt=system_prompt)
        
        try:
            clean_res = response.strip()
            if "```json" in clean_res: clean_res = clean_res.split("```json")[-1].split("```")[0]
            elif "```" in clean_res: clean_res = clean_res.split("```")[-1].split("```")[0]
            return json.loads(clean_res)
        except Exception as e:
            logger.error(f"Sales Agent: Failed to parse qualification response: {e}")
            return {
                "sales_outcome": {"status": "error", "notes": "Failed to qualify lead due to parse error."},
                "actions": []
            }

    def execute_sales_action(self, action_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatches actions based on the qualification report.
        """
        logger.info(f"Sales Agent: Executing action '{action_type}'")
        
        if action_type == "send_email":
            return self._send_email(payload)
        elif action_type == "ask_question":
            return self._handle_question(payload)
        elif action_type == "schedule_meeting":
            return self._schedule_meeting(payload)
        elif action_type == "mark_unqualified":
            return self._mark_unqualified(payload)
        elif action_type == "mark_converted":
            return self._mark_converted(payload)
        
        return {"status": "error", "message": f"Unknown action type: {action_type}"}

    # --- Internal Action Implementations ---

    def _send_email(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        subject = payload.get("subject", "Following up")
        body = payload.get("body", "")
        logger.info(f"Sales Agent: [EMAIL SENT] Subject: {subject}")
        # In a real system, this would call GMail/SendGrid
        return {"status": "success"}

    def _handle_question(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        question = payload.get("question", "")
        logger.info(f"Sales Agent: [QUESTION ASKED] {question}")
        return {"status": "success"}

    def _schedule_meeting(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Sales Agent: [MEETING BOOKED] payload: {payload}")
        return {"status": "success"}

    def _mark_unqualified(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        reason = payload.get("reason", "No reason provided")
        logger.info(f"Sales Agent: [UNQUALIFIED] {reason}")
        return {"status": "success"}

    def _mark_converted(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Sales Agent: [CONVERTED] Lead reached paid status.")
        return {"status": "success"}

    def handle_event(self, payload: Any):
        # Required by BaseAgent but we use setup_subscriptions
        pass
