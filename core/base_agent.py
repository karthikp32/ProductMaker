from typing import Any, Dict
import logging
from infrastructure.event_bus import EventBus

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Abstract base class for all agents in the system.
    """
    def __init__(self, name: str, event_bus: EventBus):
        self.name = name
        self.event_bus = event_bus
        self.setup_subscriptions()

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
