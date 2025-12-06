from abc import abstractmethod
from typing import Any, Dict
from core.base_agent import BaseAgent

class ArchitectAgentInterface(BaseAgent):
    """
    Abstract interface for the Architect Agent.
    Responsible for translating product specs into technical architecture (DB schema, APIs).
    """

    @abstractmethod
    def design_system_architecture(self, product_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Define the database schema, API endpoints, and system structure based on the product spec.
        """
        pass
