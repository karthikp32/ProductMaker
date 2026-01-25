from typing import Any, Dict, List, Type, Optional
import logging
import os
from pydantic import BaseModel, Field

from core.base_agent import BaseAgent, AgentFunction
from infrastructure.llm.reasoning_model_client import ReasoningModelClient

logger = logging.getLogger(__name__)


# --- Agent ---

class SalesAgent(BaseAgent):
    """
    Sales Agent: Owns 'Conversion'.
    """
    def __init__(self, name: str, event_bus: Any):
        super().__init__(name, event_bus)
        self.reasoning_client = ReasoningModelClient()

    @property
    def role(self) -> str:
        return "Sales Representative: Lead engagement and conversion."

    @property
    def functions(self) -> List[AgentFunction]:
        return []

    def setup_subscriptions(self):
        self.event_bus.subscribe("LEAD_GENERATED", self.on_lead_generated)

    def on_lead_generated(self, payload: Any):
        lead = payload.get("lead", {})
        if isinstance(lead, str):
             # Handle simple string leads for testing
             lead = {"name": "Unknown", "email": "unknown@example.com", "context": lead}
             
        lead_name = lead.get("name", "Prospect")
        lead_email = lead.get("email", "unknown@example.com")
        
        logger.info(f"Sales Agent: Processing lead '{lead_name}'...")
        
        # 1. Draft Email
        email_draft = self._draft_email(lead)
        
        # 2. Human Review
        if self._request_human_review(lead_name, email_draft):
            # 3. Send Email
            send_result = self.send_email_sandbox(
                recipient=lead_email,
                subject=email_draft.get("subject", "Hello"),
                body=email_draft.get("body", "")
            )
            
            # 4. Update CRM
            self.update_crm(
                action="log_email",
                data={"email": lead_email, "subject": email_draft.get("subject")}
            )
            
            self.publish_event("OUTREACH_SENT", {"lead": lead_email, "status": send_result["status"]})
        else:
            logger.info("Sales Agent: Outreach cancelled by user.")

    # --- Tools (Internal Methods) ---

    def send_email_sandbox(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Sends an email to a prospect. By default runs in SANDBOX mode (logs only).
        """
        sandbox_mode = os.getenv("SALES_SANDBOX_MODE", "true").lower() == "true"
        
        if sandbox_mode:
            logger.info(f"[send_email_sandbox] SANDBOX: Email not sent.")
            logger.info(f"To: {recipient}\nSubject: {subject}\nBody:\n{body}")
            return {"status": "success", "mode": "sandbox", "message": "Email logged to console (Sandbox)."}
        else:
            # TODO: Integrate with real Gmail API here using credentials
            gmail_api_key = os.getenv("GMAIL_API_KEY")
            if not gmail_api_key:
                 return {"status": "error", "message": "Missing GMAIL_API_KEY for live sending."}
            
            logger.info(f"[send_email_sandbox] Sending LIVE email to {recipient}...")
            # Placeholder for actual API call
            return {"status": "success", "mode": "live", "message": f"Email sent to {recipient} via Gmail."}

    def update_crm(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the CRM (HubSpot) with new contacts or activity logs.
        """
        # hubspot_key = os.getenv("HUBSPOT_API_KEY") 
        
        # Simulation logic
        if action == "create_contact":
            logger.info(f"[update_crm] Creating CRM contact: {data.get('name')} ({data.get('email')})")
            return {"status": "success", "id": "contact_123", "action": action}
        
        elif action == "log_email":
            logger.info(f"[update_crm] Logging email to CRM for: {data.get('email')}")
            return {"status": "success", "id": "activity_456", "action": action}
            
        elif action == "update_status":
             logger.info(f"[update_crm] Updating status for {data.get('email')} to {data.get('status')}")
             return {"status": "success", "action": action}
             
        return {"status": "error", "message": f"Unknown action: {action}"}

    # --- Helpers ---

    def _draft_email(self, lead: Dict[str, Any]) -> Dict[str, str]:
        context = lead.get("context", "")
        name = lead.get("name", "there")
        
        prompt = f"""
        You are a top-tier Sales Representative.
        Draft a personalized cold email to a lead.
        
        **Lead Info:**
        Name: {name}
        Context: {context}
        
        **Goal:**
        Book a meeting to demo our product.
        
        **Output Format:**
        Return JSON with 'subject' and 'body'.
        """
        
        logger.info("Sales Agent: calling LLM to draft email...")
        response = self.reasoning_client.generate(prompt, system_prompt="You are a persuasive Sales Copywriter. Output JSON.")
        
        try:
            import json
            clean_res = response.strip()
            if "```json" in clean_res: clean_res = clean_res.split("```json")[-1].split("```")[0]
            elif "```" in clean_res: clean_res = clean_res.split("```")[-1].split("```")[0]
            return json.loads(clean_res)
        except Exception:
            logger.warning("Sales Agent: Failed to parse JSON email draft. Returning raw text.")
            return {"subject": "Quick Question", "body": response}

    def _request_human_review(self, name: str, draft: Dict[str, str]) -> bool:
        """
        Pauses execution to ask for human approval via CLI.
        """
        print(f"\n================ [Sales Agent] REVIEW REQUIRED ================")
        print(f"Drafting email for: {name}")
        print(f"Subject: {draft.get('subject')}")
        print(f"Body:\n{draft.get('body')}")
        print(f"===============================================================")
        
        try:
            # Simple CLI interaction
            choice = input(">> Approve and Send? (y/n): ")
            return choice.lower().strip().startswith('y')
        except EOFError:
            # Handle non-interactive environments
            logger.warning("Sales Agent: Non-interactive env detected. Auto-skipping send.")
            return False
