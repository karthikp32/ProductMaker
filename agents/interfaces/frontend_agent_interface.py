from abc import abstractmethod
from typing import Any, Dict
from core.interfaces import Agent

class FrontendAgentInterface(Agent):
    """
    Abstract interface for the Frontend Agent.
    Responsible for building user interface components and connecting them to the backend.
    """

    @abstractmethod
    def implement_ui_components(self, architecture_doc: Dict[str, Any]) -> None:
        """
        Generate and write the frontend code (e.g., React components, HTML/CSS)
        required to visualize the product.
        """
        pass
