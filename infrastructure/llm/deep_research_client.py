import os
import logging
import time
from smolagents import CodeAgent, LiteLLMModel, Tool, GoogleSearchTool, DuckDuckGoSearchTool, VisitWebpageTool
from infrastructure.llm.llm_client import LLMClient

# Configure logging
logger = logging.getLogger(__name__)

class DeepResearchClient(LLMClient):
    """
    Client for deep research using Hugging Face smolagents 'Deep Research' pattern.
    Uses a CodeAgent that can search the web and visit pages.
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. Agent may fail.")
        
        # Initialize the model - using Gemini 2.5 Flash via LiteLLM
        self.model = LiteLLMModel(
            model_id="gemini/gemini-2.5-flash", 
            api_key=self.api_key
        )
        
        # Tools
        self.search_tool = DuckDuckGoSearchTool()
        self.visit_tool = VisitWebpageTool()
        
        # Initialize the Agent
        self.agent = CodeAgent(
            tools=[self.search_tool, self.visit_tool],
            model=self.model,
            max_steps=10, # Cap usage
            verbosity_level=1
        )

    def perform_research(self, prompt: str) -> str:
        """
        Performs deep research based on the provided prompt.
        """
        try:
            logger.info(f"Starting Deep Research...")
            result = self.agent.run(prompt)
            return str(result)
        except Exception as e:
            logger.error(f"Deep Research failed: {e}")
            return f"Error during research: {e}"

    def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.", model: str = None) -> str:
        """
        Fallback simple generation if needed, bypassing the full agent loop.
        """
        # Simple direct call via the model wrapper
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        return self.model(messages)

