from abc import abstractmethod
from typing import Any, Dict
from core.base_agent import BaseAgent

class SalesAgentInterface(BaseAgent):
    """
    Abstract interface for the Sales Agent.
    Responsible for outbound prospecting, drafting emails, and managing leads.
    """

    @abstractmethod
    def generate_outreach_copy(self, lead_context: Dict[str, Any]) -> str:
        """
        Draft a sales email or message for a specific lead context.
        """
        pass
