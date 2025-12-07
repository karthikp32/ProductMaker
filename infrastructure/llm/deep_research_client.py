import os
import logging
from typing import Dict, List
import google.generativeai as genai
from infrastructure.llm.llm_client import LLMClient

from agents.prompts.prompts import get_deep_research_system_prompt

logger = logging.getLogger(__name__)

class DeepResearchClient(LLMClient):
    """
    Client for deep research models with fallback logic.
    Prioritizes Gemini models.
    """
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found. Gemini calls may fail.")
        else:
            genai.configure(api_key=self.api_key)

        self.limits = {
            "gemini-3-pro-preview": 10,
            "gemini-2.5-pro": 50,
            "gemini-2.5-flash": 1000
        }
        self.usage: Dict[str, int] = {model: 0 for model in self.limits}
        # Priority: Best first
        self.models_priority = ["gemini-3-pro-preview", "gemini-2.5-pro", "gemini-2.5-flash"]

    def research_customer_segment(self, customer_segment: str) -> str:
        """
        Performs deep research on a specific customer segment using the specialized system prompt.
        """
        user_prompt = f"Target customer segment:\n{customer_segment}\n\nBegin deep research."
        system_prompt = get_deep_research_system_prompt(customer_segment)
        return self.generate(user_prompt, system_prompt=system_prompt)

    def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.", model: str = None) -> str:
        """
        Attempts to generate response using deep research models in priority order based on rate limits.
        """
        selected_model = self.models_priority[-1] # Default fallback (Flash)

        # Manager logic to select best available model
        for model_candidate in self.models_priority:
            current_usage = self.usage.get(model_candidate, 0)
            limit = self.limits.get(model_candidate, float('inf'))
            if current_usage < limit:
                selected_model = model_candidate
                break
        
        # Increment usage
        self.usage[selected_model] = self.usage.get(selected_model, 0) + 1
        logger.info(f"Deep Research Client using model: {selected_model} (Usage: {self.usage[selected_model]}/{self.limits.get(selected_model, 'inf')})")

        # Dispatch to specific function
        if selected_model == "gemini-3-pro-preview":
            return self.call_gemini_3_preview(prompt, system_prompt)
        elif selected_model == "gemini-2.5-pro":
            return self.call_gemini_2_5_pro(prompt, system_prompt)
        elif selected_model == "gemini-2.5-flash":
            return self.call_gemini_2_5_flash(prompt, system_prompt)
        else:
            return self.call_gemini_2_5_flash(prompt, system_prompt)

    def _call_gemini_api(self, model_name: str, prompt: str, system_prompt: str) -> str:
        """
        Helper to execute the actual API call to Google Generative AI.
        """
        try:
            # Note: system_instruction is supported in newer SDK versions
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_prompt
            )
            
            # Generate content
            response = model.generate_content(prompt)
            
            # Return text
            return response.text
        except Exception as e:
            logger.error(f"Failed to call {model_name}: {e}")
            return f"Error generating content with {model_name}: {e}"

    def call_gemini_3_preview(self, prompt: str, system_prompt: str) -> str:
        logger.info(f"Calling Gemini 3.0 Pro Preview with prompt: {prompt[:50]}...")
        # Using a likely placeholder model ID or the exact string if available in future
        # Currently mapping to the exact string requested.
        return self._call_gemini_api("gemini-3-pro-preview", prompt, system_prompt)

    def call_gemini_2_5_pro(self, prompt: str, system_prompt: str) -> str:
        logger.info(f"Calling Gemini 2.5 Pro with prompt: {prompt[:50]}...")
        return self._call_gemini_api("gemini-2.5-pro", prompt, system_prompt)

    def call_gemini_2_5_flash(self, prompt: str, system_prompt: str) -> str:
        logger.info(f"Calling Gemini 2.5 Flash with prompt: {prompt[:50]}...")
        return self._call_gemini_api("gemini-2.5-flash", prompt, system_prompt)
