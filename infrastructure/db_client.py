import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)

class DBClient:
    """
    Client for interacting with the PostgreSQL database.
    """
    def __init__(self):
        self.conn = None
        try:
            # In a real app, use env vars. For V0, we default to docker-compose values.
            self.conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                database=os.getenv("POSTGRES_DB", "productmaker"),
                user=os.getenv("POSTGRES_USER", "user"),
                password=os.getenv("POSTGRES_PASSWORD", "password")
            )
            logger.info("Connected to Database.")
        except Exception as e:
            logger.error(f"Failed to connect to Database: {e}")

    def execute(self, query: str, params: tuple = None):
        """
        Execute a write query (INSERT, UPDATE, DELETE).
        """
        if not self.conn:
            return
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                self.conn.commit()
        except Exception as e:
            logger.error(f"DB Execute Error: {e}")
            self.conn.rollback()

    def fetch_one(self, query: str, params: tuple = None):
        """
        Fetch a single row.
        """
        if not self.conn:
            return None
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchone()
        except Exception as e:
            logger.error(f"DB Fetch Error: {e}")
            return None
