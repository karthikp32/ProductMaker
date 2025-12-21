import os
import shutil
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
        super().__init__(name, event_bus)
        self.reasoning_client = ReasoningModelClient()
        self.deep_research_client = DeepResearchClient()

    @property
    def role(self) -> str:
        return "Product Manager: Analyzes market trends, defines product requirements (PRDs), and prioritizes features."

    @property
    def functions(self) -> List[AgentFunction]:
        return []

    def setup_subscriptions(self):
        self.event_bus.subscribe("SYSTEM_START", self.on_system_start)
        # These can still be triggered by events, but are now primarily called by the API directly
        self.event_bus.subscribe("SEGMENT_ANALYSIS_REQUESTED", self.analyze_segment)
        self.event_bus.subscribe("INDUSTRY_ANALYSIS_REQUESTED", self.analyze_industry)

    def handle_instruction(self, instruction: str, context: Dict[str, Any]):
        if "deep dive" in instruction.lower() or "market research" in instruction.lower():
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

    def analyze_segment(self, payload: Any):
        segment_name = payload.get("segment_name")
        target_repo_path = payload.get("target_repo_path")
        industry = payload.get("industry", "General")
        
        logger.info(f"PM Agent: Analyzing segment '{segment_name}' for industry '{industry}'...")
        
        # 1. Run Research
        research_findings = self._run_deep_research(segment_name)

        # 2. Generate Hypotheses
        hypotheses_data = self._generate_hypothesis(segment_name, research_findings)
        
        # 3. Persist Documents
        file_paths = self._persist_documents(
            industry=industry,
            segment=segment_name,
            research_findings=research_findings,
            hypotheses_analysis=hypotheses_data[0]["analysis"],
            target_repo_path=target_repo_path
        )
        
        # 4. Publish Spec
        self.publish_event("SPEC_COMPLETED", {
            "segment": segment_name, 
            "hypotheses": hypotheses_data,
            "saved_files": file_paths
        })

    def _persist_documents(self, industry: str, segment: str, research_findings: str, hypotheses_analysis: str, target_repo_path: str = None) -> Dict[str, str]:
        """
        Saves research and hypotheses to the local output folder and optionally copies them to a target repo.
        """
        # 1. Create Local Folder Structure
        safe_industry = industry.replace(" ", "_").lower()
        safe_segment = segment.replace(" ", "_").lower()
        
        local_output_dir = os.path.join("output", safe_industry, safe_segment, "product_documents")
        os.makedirs(local_output_dir, exist_ok=True)
        
        # 2. Write Files Locally
        research_file = os.path.join(local_output_dir, "market_research.md")
        hypotheses_file = os.path.join(local_output_dir, "product_hypotheses.md")
        
        with open(research_file, "w") as f:
            f.write(f"# Market Research: {segment}\n\n")
            f.write(research_findings)
            
        with open(hypotheses_file, "w") as f:
            f.write(f"# Product Hypotheses: {segment}\n\n")
            f.write(hypotheses_analysis)
            
        logger.info(f"PM Agent: Documents persisted locally to {local_output_dir}")
        
        result_paths = {
            "local_research": research_file,
            "local_hypotheses": hypotheses_file
        }
        
        # 3. Copy to Target Repo if provided
        if target_repo_path:
            # Resolve ~ if present
            target_repo_path = os.path.expanduser(target_repo_path)
            repo_doc_dir = os.path.join(target_repo_path, "product_documents")
            
            try:
                os.makedirs(repo_doc_dir, exist_ok=True)
                shutil.copy(research_file, os.path.join(repo_doc_dir, f"market_research_{safe_segment}.md"))
                shutil.copy(hypotheses_file, os.path.join(repo_doc_dir, f"product_hypotheses_{safe_segment}.md"))
                logger.info(f"PM Agent: Documents copied to target repo: {repo_doc_dir}")
                result_paths["repo_doc_dir"] = repo_doc_dir
            except Exception as e:
                logger.error(f"PM Agent: Failed to copy to target repo {target_repo_path}: {e}")
                
        return result_paths

    def analyze_industry(self, payload: Any):
        industry = payload.get("industry")
        target_repo_path = payload.get("target_repo_path")
        
        logger.info(f"PM Agent: Initiating high-level analysis for Industry: '{industry}'...")
        
        # 1. Broad Market Research for the Industry
        research_findings = self._analyze_industry_landscape(industry)
        
        # 2. Prioritization & Economic Deep Dive
        prioritization_report = self._prioritize_segments(industry, research_findings)
        
        # 3. Persist Industry Report
        report_paths = self._persist_industry_report(
            industry=industry,
            research_findings=research_findings,
            prioritization_report=prioritization_report,
            target_repo_path=target_repo_path
        )
        
        self.publish_event("INDUSTRY_SPEC_COMPLETED", {
            "industry": industry,
            "saved_files": report_paths
        })

    def _analyze_industry_landscape(self, industry: str) -> str:
        """
        Researches the broad industry to identify key customer segments.
        """
        prompt = f"""
        You are an expert Market Strategist. 
        Research the following industry: "{industry}".
        
        Your goal is to identify:
        1. The main customer types/segments within this industry.
        2. Rough estimates of their technology spend or budget for new tools.
        3. Current trends or shifts creating new opportunities.
        4. High-level competitive landscape.
        
        Synthesize this into a market landscape report.
        """
        return self.deep_research_client.perform_research(prompt)

    def _prioritize_segments(self, industry: str, landscape_research: str) -> str:
        """
        Uses reasoning to prioritize segments based on profit potential and likelihood to pay.
        """
        prompt = f"""
        Based on the landscape research for the '{industry}' industry below, identify and prioritize the top 3-5 customer segments for a new software product.
        
        **Landscape Research:**
        {landscape_research}
        
        **Prioritization Framework:**
        For each segment, analyze:
        1. **Likelihood to Pay:** Do they have budget? Are they currently paying for solutions?
        2. **Potential Revenue:** Ticket size vs. Volume.
        3. **Scalability:** Total Addressable Market (TAM).
        4. **Implementation Costs/Difficulty:** How hard is it to build for them?
        5. **Overall Profit Potential Score (1-10).**
        
        **Output:**
        Provide a prioritized list with clear justifications for why the #1 segment is the best starting point.
        """
        return self.reasoning_client.generate(prompt, system_prompt="You are a Ruthless Private Equity Analyst and Product Strategist.")

    def _persist_industry_report(self, industry: str, research_findings: str, prioritization_report: str, target_repo_path: str = None) -> Dict[str, str]:
        safe_industry = industry.replace(" ", "_").lower()
        local_output_dir = os.path.join("output", safe_industry, "market_landscape")
        os.makedirs(local_output_dir, exist_ok=True)
        
        research_file = os.path.join(local_output_dir, "landscape_research.md")
        prioritization_file = os.path.join(local_output_dir, "segment_prioritization.md")
        
        with open(research_file, "w") as f:
            f.write(f"# Industry Landscape: {industry}\n\n{research_findings}")
        with open(prioritization_file, "w") as f:
            f.write(f"# Segment Prioritization: {industry}\n\n{prioritization_report}")
            
        logger.info(f"PM Agent: Industry reports persisted to {local_output_dir}")
        
        result_paths = {"local_landscape": research_file, "local_prioritization": prioritization_file}
        
        if target_repo_path:
            target_repo_path = os.path.expanduser(target_repo_path)
            repo_doc_dir = os.path.join(target_repo_path, "product_documents", "market_landscape")
            try:
                os.makedirs(repo_doc_dir, exist_ok=True)
                shutil.copy(research_file, os.path.join(repo_doc_dir, "landscape_research.md"))
                shutil.copy(prioritization_file, os.path.join(repo_doc_dir, "segment_prioritization.md"))
                result_paths["repo_landscape_dir"] = repo_doc_dir
            except Exception as e:
                logger.error(f"PM Agent: Failed to copy industry reports: {e}")
                
        return result_paths

    def _check_data_freshness(self, segment_name: str) -> bool:
        query = "SELECT last_updated FROM research_data WHERE segment = %s"
        result = self.db.fetch_one(query, (segment_name,))
        return True if result else False

    def _run_deep_research(self, topic: str) -> str:
        logger.info(f"PM Agent: Deep Researching {topic}...")
        response = self.research_customer_segment(topic)
        logger.info(f"PM Agent: Research result: {response[:100]}... (truncated)")
        return response

    def research_customer_segment(self, customer_segment: str) -> str:
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
        return [{"segment": segment_name, "analysis": response}]
