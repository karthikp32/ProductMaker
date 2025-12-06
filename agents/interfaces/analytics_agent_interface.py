from abc import abstractmethod
from typing import Any, Dict
from core.interfaces import Agent

class AnalyticsAgentInterface(Agent):
    """
    Abstract interface for the Analytics Agent.
    Responsible for interpreting data, running reports, and verifying success metrics.
    """

    @abstractmethod
    def analyze_experiment_data(self, experiment_id: str) -> Dict[str, Any]:
        """
        Calculate statistics and ROI for a completed experiment to determine success.
        """
        pass
