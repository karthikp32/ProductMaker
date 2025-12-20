import os
import logging
from typing import Dict, List, Any
from litellm import completion
from infrastructure.llm.llm_client import LLMClient

logger = logging.getLogger(__name__)

class ReasoningModelClient(LLMClient):
    """
    Client for reasoning models using DeepSeek R1 via OpenRouter.
    """
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_DEEPSEEK_R1_API_KEY")
        
        if not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY not found.")
        if not self.openrouter_api_key:
            logger.warning("OPENROUTER_DEEPSEEK_R1_API_KEY not found.")
        
        # Priority order of models
        self.models = [
            {"id": "gemini/gemini-3-flash-preview", "api_key": self.gemini_api_key},
            {"id": "openrouter/deepseek/deepseek-r1-0528:free", "api_key": self.openrouter_api_key}
        ]

    def generate(self, prompt: str, system_prompt: str = "You are a Visionary Product Leader.", model: str = None) -> str:
        """
        Generates a response using reasoning models with fallback.
        """
        for model_info in self.models:
            model_id = model_info["id"]
            api_key = model_info["api_key"]
            
            if not api_key:
                logger.info(f"Skipping {model_id} (missing API key)")
                continue

            try:
                logger.info(f"Reasoning Client: Attempting with {model_id}...")
                response = completion(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    api_key=api_key
                )
                
                content = response.choices[0].message.content
                
                # Remove thinking tags if present (common in DeepSeek R1)
                if "<think>" in content and "</think>" in content:
                    content = content.split("</think>")[-1].strip()
                
                return content
                
            except Exception as e:
                logger.error(f"Reasoning Model call failed for {model_id}: {e}")
                continue # Try next model
        
        return "Error: All reasoning models failed or were missing API keys."
