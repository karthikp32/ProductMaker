from abc import abstractmethod
from typing import Any, Dict
from core.interfaces import Agent

class PMAgentInterface(Agent):
    """
    Abstract interface for the Product Manager Agent.
    Responsible for market research, hygiene checks, and defining product specifications.
    """
    
    @abstractmethod
    def run_deep_research(self, topic: str) -> Dict[str, Any]:
        """
        Conduct deep research on a market segment or topic.
        """
        pass

    @abstractmethod
    def generate_spec_hypothesis(self, segment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a product specification or hypothesis based on gathered research.
        """
        pass
