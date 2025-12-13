import os
import logging
import time
from smolagents import CodeAgent, LiteLLMModel, Tool, DuckDuckGoSearchTool, VisitWebpageTool
from infrastructure.llm.llm_client import LLMClient

# Configure logging
logger = logging.getLogger(__name__)

class DeepResearchClient(LLMClient):
    """
    Client for deep research using Hugging Face smolagents 'Deep Research' pattern.
    Uses a CodeAgent that can search the web and visit pages.
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") # We can use Gemini with LiteLLM
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. Agent may fail.")
        
        # Initialize the model - using Gemini via LiteLLM
        # Ensure you have the `google-generativeai` package installed
        self.model = LiteLLMModel(
            model_id="gemini/gemini-2.5-pro", 
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

    def research_customer_segment(self, customer_segment: str) -> str:
        """
        Performs market research on a specific customer segment.
        """
        prompt = f"""
        You are an expert Market Researcher.
        Your goal is to gather deep insights about the following customer segment: "{customer_segment}".
        
        Please search for and analyze:
        1.  Typical persona profiles and job titles.
        2.  Core pain points and daily challenges.
        3.  Existing solutions and their gaps.
        4.  Where they hang out online (e.g., specific Subreddits, Forums, Discords).
        5.  Willingness to pay for tools (look for pricing of similar tools).

        Use your tools to search the web and visit promising pages.
        Synthesize all your findings into a comprehensive report.
        """
        
        try:
            logger.info(f"Starting Market Research for: {customer_segment}")
            result = self.agent.run(prompt)
            return str(result)
        except Exception as e:
            logger.error(f"Market Research failed: {e}")
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

