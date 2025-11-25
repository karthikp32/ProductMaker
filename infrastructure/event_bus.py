import logging
from typing import Callable, Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventBus:
    """
    A simple in-memory Event Bus for decoupling agents.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Any], None]):
        """
        Register a callback function for a specific event type.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.info(f"Subscribed to event: {event_type}")

    def publish(self, event_type: str, payload: Any = None):
        """
        Publish an event to all subscribers.
        """
        logger.info(f"Publishing event: {event_type} | Payload: {payload}")
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(payload)
                except Exception as e:
                    logger.error(f"Error in subscriber for {event_type}: {e}")
        else:
            logger.warning(f"No subscribers for event: {event_type}")
