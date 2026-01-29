from abc import abstractmethod
from typing import Any, Dict, List
from core.base_agent import BaseAgent

class SalesAgentInterface(BaseAgent):
    """
    Abstract interface for the Sales Agent.
    Responsible for qualifying leads and driving bottom-of-funnel conversions.
    """

    @abstractmethod
    def qualify_lead(self, handoff_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a lead based on BANT (Budget, Authority, Need, Timeline) or similar criteria.
        Returns a qualification report and recommended actions.
        """
        pass

    @abstractmethod
    def execute_sales_action(self, action_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific sales action such as sending an email or scheduling a meeting.
        """
        pass
