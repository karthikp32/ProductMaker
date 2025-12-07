import logging
from typing import Dict, List
from infrastructure.llm.llm_client import LLMClient

logger = logging.getLogger(__name__)

class ReasoningModelClient(LLMClient):
    """
    Client for reasoning models with fallback logic.
    """
    def __init__(self):
        self.limits = {
            "o1-preview": 10,
            "o1-mini": 50,
            "gpt-4o": 1000
        }
        self.usage: Dict[str, int] = {model: 0 for model in self.limits}
        self.models_priority = ["o1-preview", "o1-mini", "gpt-4o"]

    def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.", model: str = None) -> str:
        """
        Attempts to generate response using reasoning models in priority order based on rate limits.
        """
        # If a specific model is requested, try to use it (basic support)
        # But primarily logic is to use the best available from priority list
        selected_model = self.models_priority[-1] # Default fallback

        # Manager logic to select best available model
        for model_candidate in self.models_priority:
            current_usage = self.usage.get(model_candidate, 0)
            limit = self.limits.get(model_candidate, float('inf'))
            if current_usage < limit:
                selected_model = model_candidate
                break
        
        # Increment usage
        self.usage[selected_model] = self.usage.get(selected_model, 0) + 1
        logger.info(f"Reasoning Client using model: {selected_model} (Usage: {self.usage[selected_model]}/{self.limits.get(selected_model, 'inf')})")

        return self._execute_call(selected_model, prompt, system_prompt)

    def _execute_call(self, model: str, prompt: str, system_prompt: str) -> str:
        """
        Simulate the actual API call.
        """
        logger.info(f"LLM Call ({model}): {prompt[:50]}...")
        return f"[MOCK {model} RESPONSE] Processed: {prompt[:20]}..."
