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
            self.research_customer_segment(topic)
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
        research_findings = self.research_customer_segment(segment_name)

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
        
        logger.info(f"PM Agent: Initiating end-to-end analysis for Industry: '{industry}'...")
        
        # 1. Broad Market Research for the Industry
        landscape_findings = self._analyze_industry_landscape(industry)
        
        # 2. Prioritization & Economic Deep Dive
        prioritization_report = self._prioritize_segments(industry, landscape_findings)
        
        # 3. Save the High-Level Report
        report_paths = self._persist_industry_report(
            industry=industry,
            research_findings=landscape_findings,
            prioritization_report=prioritization_report,
            target_repo_path=target_repo_path
        )
        
        # 4. Prepare Top 2 Segments with YAML Contexts
        segment_deep_dives = self._prepare_segment_deep_dives(industry, landscape_findings, prioritization_report)
        logger.info(f"PM Agent: Prepared {len(segment_deep_dives)} segment deep-dives.")
        
        # 5. Process each segment
        for dive in segment_deep_dives:
            segment_name = dive.get("name")
            segment_yaml_context = dive.get("yaml_context")
            
            logger.info(f"PM Agent: Starting deep-dive for segment: {segment_name}")
            
            # 5a. Segment Research
            segment_research = self.research_customer_segment(segment_name)
            
            # 5b. Generate 5 Hypotheses using the YAML context
            hypotheses = self._generate_hypothesis(segment_name, segment_research, segment_yaml_context)
            
            # 5c. Save the collective Hypotheses document for this segment
            # We include the YAML context in the document for transparency
            self._persist_segment_hypotheses_doc(
                industry=industry,
                segment=segment_name,
                hypotheses=hypotheses,
                research_findings=segment_research,
                yaml_context=segment_yaml_context,
                target_repo_path=target_repo_path
            )
            
            # 5d. For each hypothesis, generate a full PRD
            for hyp in hypotheses:
                logger.info(f"PM Agent: Generating PRD for hypothesis: {hyp.get('name', 'Idea')}")
                prd_content = self._generate_prd(industry, segment_name, hyp, segment_research, segment_yaml_context)
                
                # 5e. Persist individual PRD
                self._persist_segment_prd(
                    industry=industry,
                    segment=segment_name,
                    hypothesis_name=hyp.get('name', 'Idea'),
                    research_findings=segment_research,
                    prd_content=prd_content,
                    target_repo_path=target_repo_path
                )
        
        self.publish_event("INDUSTRY_WORKFLOW_COMPLETED", {
            "industry": industry,
            "segments_processed": [d.get("name") for d in segment_deep_dives]
        })

    def _prepare_segment_deep_dives(self, industry: str, landscape_research: str, prioritization_report: str) -> List[Dict[str, Any]]:
        """
        Uses LLM to pick top 2 segments and create YAML contexts for them.
        Returns a list of segments with their name and yaml context.
        """
        prompt = f"""
        Given the industry '{industry}', analyze the research and prioritization report below.
        1. Select the TOP 2 most promising customer segments.
        2. For each, create a concise 'Segment Strategic Context' in YAML format.
        
        **Prioritization Report:**
        {prioritization_report}
        
        **Landscape Research:**
        {landscape_research[:4000]}
        
        **Output Format (Strictly follow this for 2 segments):**
        ---
        NAME: [Exact Segment Name]
        YAML:
        [YAML Context Here]
        ---
        """
        response = self.reasoning_client.generate(prompt, system_prompt="You are a Strategic Analyst.")
        
        dives = []
        try:
            logger.info(f"PM Agent: Received strategy response: {response[:200]}...")
            
            # Simple manual parser for the delimited format
            blocks = response.split("---")
            for block in blocks:
                block = block.strip()
                if not block: continue
                
                if "NAME:" in block:
                    name = ""
                    yaml_content = []
                    is_yaml = False
                    
                    for line in block.split("\n"):
                        clean_line = line.strip()
                        if clean_line.upper().startswith("NAME:"):
                            name = clean_line[5:].strip().strip("[]").strip()
                        elif clean_line.upper().startswith("YAML:"):
                            is_yaml = True
                        elif is_yaml:
                            yaml_content.append(line) # Keep original line for YAML indentation
                    
                    if name:
                        yaml_str = "\n".join(yaml_content).strip()
                        if not yaml_str:
                             yaml_str = "context: No specific context provided."
                             
                        dives.append({
                            "name": name,
                            "yaml_context": yaml_str
                        })
                        logger.info(f"PM Agent: Extracted segment: {name}")
            
            if not dives:
                logger.warning("PM Agent: Manual segment parsing failed. Trying one last heuristic.")
                # Heuristic: split by lines and look for "NAME:" anywhere
                for line in response.split("\n"):
                    if "NAME:" in line.upper() and len(dives) < 2:
                        name = line.split(":", 1)[1].strip().strip("[]").strip()
                        if name:
                            dives.append({"name": name, "yaml_context": "context: Extracted via fallback."})
                
        except Exception as e:
            logger.error(f"Failed to prepare segment deep-dives: {e}")
            
        return dives[:2]

    def _generate_prd(self, industry: str, segment: str, hypothesis: Dict[str, Any], research_findings: str, yaml_context: str = "") -> str:
        prompt = f"""
        You are a Senior Product Manager. Write a detailed Product Requirements Document (PRD).

        **Context:**
        Industry: {industry}
        Target Segment: {segment}
        Segment Strategy (YAML): 
        {yaml_context}
        
        **Product Concept:**
        - Name: {hypothesis.get('name', 'New Tool')}
        - Problem: {hypothesis.get('problem', 'See research')}
        - Value Prop: {hypothesis.get('value_prop', 'See research')}
        - Key Features: {hypothesis.get('features', [])}
        
        **Detailed Research Findings:**
        {research_findings}
        
        **PRD Structure Requirements:**
        1. **Overview**: Briefly describe what this product is and why it is being built.
        2. **Success Metrics**: Define the key metrics (KPIs) for internal goals.
        3. **Personas**: Identify target personas; specify the Primary Persona.
        4. **User Scenarios**: End-to-end stories of personas using the product in real contexts.
        5. **User Stories / Features / Requirements**: Prioritized features with justifications.
        6. **Features Out (Non-Goals)**: What is intentionally excluded and why.
        7. **Open Issues**: Unresolved questions, risks, or areas for research.
        
        Format in professional Markdown.
        """
        return self.reasoning_client.generate(prompt, system_prompt="You are an Elite Product Manager at a Tier-1 Tech Firm.")

    def _persist_segment_prd(self, industry: str, segment: str, hypothesis_name: str, research_findings: str, prd_content: str, target_repo_path: str = None):
        safe_industry = industry.replace(" ", "_").lower()
        safe_segment = segment.replace(" ", "_").lower()
        safe_hyp = hypothesis_name.replace(" ", "_").lower().replace("/", "_")
        
        local_dir = os.path.join("output", safe_industry, safe_segment, "prds")
        os.makedirs(local_dir, exist_ok=True)
        
        prd_file = os.path.join(local_dir, f"prd_{safe_hyp}.md")
        research_file = os.path.join(local_dir, "segment_research.md")
        
        with open(prd_file, "w") as f: f.write(prd_content)
        if not os.path.exists(research_file):
            with open(research_file, "w") as f: f.write(research_findings)
        
        if target_repo_path:
            target_repo_path = os.path.expanduser(target_repo_path)
            repo_prd_dir = os.path.join(target_repo_path, "product_documents", safe_industry, safe_segment)
            try:
                os.makedirs(repo_prd_dir, exist_ok=True)
                shutil.copy(prd_file, os.path.join(repo_prd_dir, f"prd_{safe_hyp}.md"))
                if not os.path.exists(os.path.join(repo_prd_dir, "market_research.md")):
                    shutil.copy(research_file, os.path.join(repo_prd_dir, "market_research.md"))
            except Exception as e:
                logger.error(f"PM Agent: Failed to copy PRD to repo: {e}")

    def _persist_segment_hypotheses_doc(self, industry: str, segment: str, hypotheses: List[Dict[str, Any]], research_findings: str, yaml_context: str = "", target_repo_path: str = None):
        safe_industry = industry.replace(" ", "_").lower()
        safe_segment = segment.replace(" ", "_").lower()
        
        local_dir = os.path.join("output", safe_industry, safe_segment)
        os.makedirs(local_dir, exist_ok=True)
        
        hyp_file = os.path.join(local_dir, "product_hypotheses.md")
        
        content = f"# Product Hypotheses for {segment}\n\n"
        content += "## Segment Strategic Context (YAML)\n"
        content += "```yaml\n" + yaml_context + "\n```\n\n"
        content += "## Research Summary\n"
        content += research_findings[:2000] + "...\n\n"
        content += "## Hypotheses\n\n"
        
        for i, hyp in enumerate(hypotheses, 1):
            content += f"### {i}. {hyp.get('name')}\n"
            content += f"**Problem:** {hyp.get('problem')}\n\n"
            content += f"**Value Prop:** {hyp.get('value_prop')}\n\n"
            content += "**Key Features:**\n"
            for feat in hyp.get("features", []):
                content += f"- {feat}\n"
            content += "\n---\n\n"
            
        with open(hyp_file, "w") as f:
            f.write(content)
            
        if target_repo_path:
            target_repo_path = os.path.expanduser(target_repo_path)
            repo_dir = os.path.join(target_repo_path, "product_documents", safe_industry, safe_segment)
            try:
                os.makedirs(repo_dir, exist_ok=True)
                shutil.copy(hyp_file, os.path.join(repo_dir, "product_hypotheses.md"))
            except Exception as e:
                logger.error(f"PM Agent: Failed to copy hypotheses doc: {e}")

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

    def _generate_hypothesis(self, segment_name: str, research_findings: str, yaml_context: str = "") -> List[Dict[str, Any]]:
        logger.info(f"PM Agent: Generating structured hypotheses for {segment_name}...")
        
        prompt = f"""
        Based on the segment context (YAML) and market research below, generate 5 distinct product ideas ranging from incremental to disruptive.
        
        **Segment Context (YAML):**
        {yaml_context}

        **Research Findings:**
        {research_findings}

        **Output Requirement:**
        Return ONLY a JSON list of objects: 
        [
          {{
            "name": "Catchy name",
            "problem": "Core pain point",
            "value_prop": "Value proposition",
            "features": ["Feature 1", "Feature 2", "Feature 3"]
          }},
          ...
        ]
        """
        
        response = self.reasoning_client.generate(prompt, system_prompt="You are a Visionary Product Strategist. Output JSON.")
        try:
            import json
            clean_res = response.strip()
            if "```json" in clean_res: clean_res = clean_res.split("```json")[-1].split("```")[0]
            elif "```" in clean_res: clean_res = clean_res.split("```")[-1].split("```")[0]
            return json.loads(clean_res)
        except Exception as e:
            logger.error(f"Failed to parse hypotheses: {e}")
            return [{"name": "Standard Solution", "problem": "Inefficiency", "value_prop": "Automated workflows", "features": ["Feature A", "Feature B"]}]
