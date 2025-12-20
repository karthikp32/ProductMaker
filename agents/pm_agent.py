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
        
        # 1. Check Freshness and run research if needed
        research_findings = None
        is_fresh = self._check_data_freshness(segment_name)
        
        if not is_fresh:
            logger.info("PM Agent: Data stale or missing. Initiating Deep Research...")
            research_findings = self._run_deep_research(segment_name)
        else:
            logger.info("PM Agent: Data fresh. Fetching research from DB...")
            # For demonstration, we'll just use a mock if 'fresh' for now
            research_findings = "Existing research findings from DB..."

        # 2. Generate Hypotheses (using the research findings)
        hypotheses = self._generate_hypothesis(segment_name, research_findings)
        
        # 3. Publish Spec
        self.publish_event("SPEC_COMPLETED", {"segment": segment_name, "hypotheses": hypotheses})

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

    def _run_deep_research(self, topic: str) -> str:
        """
        Uses DeepResearchClient to gather comprehensive information.
        """
        logger.info(f"PM Agent: Deep Researching {topic}...")
        
        # Use specialized research method for customer segments
        response = self.research_customer_segment(topic)
        
        # In a real app, we would save 'response' to the DB here.
        logger.info(f"PM Agent: Research result: {response[:100]}... (truncated)")
        # self.db.execute("INSERT INTO research_data ...")
        return response

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
        return self.deep_research_client.perform_research(prompt)

    def _generate_hypothesis(self, segment_name: str, research_findings: str) -> List[Dict[str, Any]]:
        """
        Uses ReasoningModelClient to synthesize research and form 5 distinct hypotheses.
        """
        logger.info(f"PM Agent: Generating 5 hypotheses for {segment_name}...")
        
        prompt = f"""
        Based on the follow market research findings for the customer segment '{segment_name}', 
        generate 5 distinct and innovative product hypotheses.

        **Market Research Findings:**
        {research_findings}

        **Instructions:**
        1. Each hypothesis should solve a specific pain point identified in the research.
        2. For each hypothesis, provide:
           - A catchy Name
           - The Core Problem it solves
           - The Value Proposition
           - 3 Key Features
        3. Ensure the hypotheses range from 'incremental' to 'disruptive'.

        Return the response as a structured list.
        """
        
        response = self.reasoning_client.generate(prompt, system_prompt="You are a Visionary Product Leader and Strategist.")
        
        # In a real app, we'd parse this into a list of objects.
        # For now, we return the raw response in a list wrapper or simple split.
        return [{"segment": segment_name, "analysis": response}]
