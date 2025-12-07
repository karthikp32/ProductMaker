from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type
import logging
from pydantic import BaseModel
from infrastructure.event_bus import EventBus

logger = logging.getLogger(__name__)

from infrastructure.db_client import DBClient
from infrastructure.llm.llm_client import LLMClient

class AgentFunction(ABC):
    """
    Abstract base class representing a specific capability or tool
    that an Agent can execute.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The unique name of the function (e.g., 'search_web', 'query_database').
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        A natural language description of what the function does,
        used by the Agent/LLM to understand when to call it.
        """
        pass

    @property
    @abstractmethod
    def args_schema(self) -> Type[BaseModel]:
        """
        A Pydantic model class defining the expected arguments.
        """
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        The implementation of the function logic.

        Args:
            **kwargs: Arguments matching the fields in args_schema.

        Returns:
            The result of the function execution.
        """
        pass

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    """
    def __init__(self, name: str, event_bus: EventBus):
        self.name = name
        self.event_bus = event_bus
        self.db = DBClient()
        self.llm = None # LLMClient is abstract, specific agents should instantiate their specific clients
        self.setup_subscriptions()
        # Subscribe to instructions
        self.event_bus.subscribe(f"INSTRUCT_{self.name.upper()}", self._on_instruction_received)

    def _on_instruction_received(self, payload: Dict[str, Any]):
        """
        Base handler for instructions.
        """
        instruction = payload.get("instruction")
        context = payload.get("context", {})
        logger.info(f"[{self.name}] Received instruction: {instruction}")
        self.handle_instruction(instruction, context)

    def handle_instruction(self, instruction: str, context: Dict[str, Any]):
        """
        Override this to handle specific instructions.
        """
        logger.warning(f"[{self.name}] Instruction handler not implemented.")

    @property
    @abstractmethod
    def role(self) -> str:
        """
        A description of the agent's role and responsibilities.
        """
        pass

    @property
    @abstractmethod
    def functions(self) -> List[AgentFunction]:
        """
        A list of functions (tools) that this agent is capable of using.
        """
        pass

    def setup_subscriptions(self):
        """
        Override this method to subscribe to relevant events.
        """
        pass

    def publish_event(self, event_type: str, payload: Dict[str, Any]):
        """
        Helper to publish events with agent metadata.
        """
        logger.info(f"[{self.name}] Publishing {event_type}")
        self.event_bus.publish(event_type, payload)

    def handle_event(self, payload: Any):
        """
        Main handler logic. Override this in subclasses.
        """
        raise NotImplementedError("Agents must implement handle_event")
