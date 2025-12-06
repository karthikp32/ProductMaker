from abc import abstractmethod
from typing import Any, Dict
from core.interfaces import Agent

class SalesAgentInterface(Agent):
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
