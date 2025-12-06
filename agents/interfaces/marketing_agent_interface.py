from abc import abstractmethod
from typing import Any, Dict
from core.base_agent import BaseAgent

class MarketingAgentInterface(BaseAgent):
    """
    Abstract interface for the Marketing Agent.
    Responsible for creating content, ad copy, and campaigns to drive awareness.
    """

    @abstractmethod
    def generate_launch_campaigns(self, product_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create marketing copy for various channels (Twitter, Reddit, etc.) based on the product.
        """
        pass
