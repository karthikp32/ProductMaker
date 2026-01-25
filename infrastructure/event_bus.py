import os
import logging
import json
import time
import psycopg2
from typing import Callable, Dict, List, Any
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventBus:
    """
    A persistent Event Bus backed by PostgreSQL 'task_queue' table.
    """
    def __init__(self, db_url: str = None):
        if db_url is None:
            db_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/productmaker")
        self.db_url = db_url
        self._subscribers: Dict[str, List[Callable]] = {}
        # In a real system, we'd have a separate worker loop polling this.
        # For this V0, we might need to manually trigger 'poll' or run it in a thread.

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
        Publish an event to the persistent queue.
        """
        logger.info(f"Publishing event to DB: {event_type} | Payload: {payload}")
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO task_queue (topic, payload, status)
                VALUES (%s, %s, 'PENDING')
            """, (event_type, json.dumps(payload) if payload else '{}'))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to publish event to DB: {e}")
        
        # Always trigger in-memory subscribers for V0 robustness
        self._notify_local_subscribers(event_type, payload)

    def _notify_local_subscribers(self, event_type: str, payload: Any):
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(payload)
                except Exception as e:
                    logger.error(f"Error in local subscriber for {event_type}: {e}")

