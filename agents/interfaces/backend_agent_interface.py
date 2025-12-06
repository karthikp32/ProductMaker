from abc import abstractmethod
from typing import Any, Dict
from core.interfaces import Agent

class BackendAgentInterface(Agent):
    """
    Abstract interface for the Backend Agent.
    Responsible for implementing the core logic, API handlers, and database interactions.
    """

    @abstractmethod
    def implement_api_logic(self, architecture_doc: Dict[str, Any]) -> None:
        """
        Generate and write the backend code (e.g., FastAPI handlers, DB queries) 
        matching the provided architecture.
        """
        pass
