from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class LLMClient(ABC):
    """
    Abstract interface for LLM interactions.
    """
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.", model: str = None) -> str:
        pass
