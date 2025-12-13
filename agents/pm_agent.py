from typing import Any, Dict, List
import logging
from core.base_agent import BaseAgent, AgentFunction
from infrastructure.llm.reasoning_model_client import ReasoningModelClient
from infrastructure.llm.deep_research_client import DeepResearchClient
from infrastructure.llm.llm_client import LLMClient
from infrastructure.event_bus import EventBus

logger = logging.getLogger(__name__)

class PMAgent(BaseAgent):
    """
    Product Manager Agent: Owns the 'Why' and 'What'.
    Responsible for market research, defining features, and generating hypotheses.
    """
    def __init__(self, name: str, event_bus: EventBus):
        # Initialize specialized clients before super().__init__ triggers setup_subscriptions/etc if needed
        # But BaseAgent calls setup_subscriptions in __init__, so we can just init them after or before.
        # Ideally we want them available.
        super().__init__(name, event_bus)
        self.reasoning_client = ReasoningModelClient()
        self.deep_research_client = DeepResearchClient()

    @property
    def role(self) -> str:
        return "Product Manager: Analyzes market trends, defines product requirements (PRDs), and prioritizes features."

    @property
    def functions(self) -> List[AgentFunction]:
        return [] # Add specific AgentFunctions if needed, currently empty as we use event handlers

    def setup_subscriptions(self):
        self.event_bus.subscribe("SYSTEM_START", self.on_system_start)
        self.event_bus.subscribe("SEGMENT_ANALYSIS_REQUESTED", self.on_segment_request)

    def handle_instruction(self, instruction: str, context: Dict[str, Any]):
        if "deep dive" in instruction.lower() or "market research" in instruction.lower():
            # Extract topic from instruction
            topic = instruction
            for keyword in ["deep dive", "market research", "about", "do a"]:
                topic = topic.replace(keyword, "")
            topic = topic.strip()
            
            logger.info(f"PM Agent: Starting Deep Dive on '{topic}'...")
            self._run_deep_research(topic)
            self.publish_event("RESEARCH_COMPLETED", {"topic": topic, "findings": f"Research on {topic} completed."})
        else:
            logger.warning(f"PM Agent: Unknown instruction: {instruction}")

    def on_system_start(self, payload: Any):
        logger.info("PM Agent online. Waiting for instructions.")

    def on_segment_request(self, payload: Any):
        segment_name = payload.get("segment_name")
        logger.info(f"PM Agent: Analyzing segment '{segment_name}'...")
        
        # 1. Check Freshness
        is_fresh = self._check_data_freshness(segment_name)
        
        if not is_fresh:
            logger.info("PM Agent: Data stale or missing. Initiating Deep Research...")
            self._run_deep_research(segment_name)
        else:
            logger.info("PM Agent: Data fresh. Skipping research.")

        # 2. Generate Hypothesis
        hypothesis_data = self._generate_hypothesis(segment_name)
        
        # 3. Publish Spec
        self.publish_event("SPEC_COMPLETED", {"spec": hypothesis_data})

    def _check_data_freshness(self, segment_name: str) -> bool:
        """
        Checks if we have recent research data for the given segment.
        """
        # In a real scenario, we would check the database for recent entries.
        # For now, we'll assume it's always stale to force research for demonstration.
        query = "SELECT last_updated FROM research_data WHERE segment = %s"
        result = self.db.fetch_one(query, (segment_name,))
        
        if result:
            # Check if timestamp is within T (e.g., 7 days)
            # For now just return True if it exists
            return True
        return False

    def _run_deep_research(self, topic: str):
        """
        Uses DeepResearchClient to gather comprehensive information.
        """
        logger.info(f"PM Agent: Deep Researching {topic}...")
        
        # Use simple heuristic to determine if we should look for a customer segment specifically
        # For now, we treat 'topic' as the customer segment or market area.
        response = self.deep_research_client.research_customer_segment(topic)
        
        # In a real app, we would save 'response' to the DB here.
        logger.info(f"PM Agent: Research result: {response}... (truncated)")
        # self.db.execute("INSERT INTO research_data ...")

    def _generate_hypothesis(self, segment_name: str) -> dict:
        """
        Uses ReasoningModelClient to synthesize research and form a hypothesis.
        """
        logger.info(f"PM Agent: Generating hypothesis for {segment_name}...")
        prompt = f"Based on general market knowledge (simulated), generate a product hypothesis for the segment: {segment_name}. Include the hypothesis and 3 key features."
        
        response = self.reasoning_client.generate(prompt, system_prompt="You are a Visionary Product Leader.")
        
        # Simple parsing logic (mocked structure for the LLM response)
        # In production, we'd ask for JSON output or structure the text carefully.
        return {
            "segment": segment_name,
            "hypothesis_summary": response[:200], # Storing a snippet of the reasoning
            "full_analysis": response
        }
