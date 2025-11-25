import os
import logging
# from openai import OpenAI # Commented out until installed

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Client for interacting with LLMs (OpenAI).
    """
    def __init__(self):
        # self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        pass

    def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        """
        Generate text from an LLM.
        """
        logger.info(f"LLM Call: {prompt[:50]}...")
        # Mock response for V0 to avoid API costs/errors during dev
        return f"[MOCK LLM RESPONSE] Processed: {prompt[:20]}..."
