from typing import Any, Dict, List, Type
import logging
import os
from pydantic import BaseModel, Field
from core.base_agent import BaseAgent, AgentFunction
from infrastructure.llm.reasoning_model_client import ReasoningModelClient
from infrastructure.event_bus import EventBus

logger = logging.getLogger(__name__)

class GenerateCopySchema(BaseModel):
    prompt: str = Field(..., description="Prompt for the copy generation")
    tone: str = Field("professional", description="Tone of the copy (e.g., professional, bold, witty)")
    platform: str = Field("landing_page", description="Platform for the copy (e.g., landing_page, ad, twitter, reddit)")

class GenerateCopyFunction(AgentFunction):
    def __init__(self, llm_client: ReasoningModelClient):
        self.llm_client = llm_client

    @property
    def name(self) -> str:
        return "generate_copy"

    @property
    def description(self) -> str:
        return "Generates high-converting marketing copy for various platforms by channeling elite marketing minds."

    @property
    def args_schema(self) -> Type[BaseModel]:
        return GenerateCopySchema

    def execute(self, **kwargs) -> str:
        prompt = kwargs.get("prompt")
        tone = kwargs.get("tone")
        platform = kwargs.get("platform")
        
        system_prompt = (
            f"You are a world-class growth marketer with the strategic vision of Steve Jobs "
            f"and the disruptive energy of Elon Musk. You focus on 'Awareness' and 'Impact'. "
            f"Tone: {tone}. Platform: {platform}."
        )
        return self.llm_client.generate(prompt, system_prompt=system_prompt)

class PostToSocialSandboxSchema(BaseModel):
    platform: str = Field(..., description="Social platform (reddit, x)")
    content: str = Field(..., description="Content to post")
    subreddit: str = Field(None, description="Subreddit for Reddit posts")

class PostToSocialSandboxFunction(AgentFunction):
    @property
    def name(self) -> str:
        return "post_to_social_sandbox"

    @property
    def description(self) -> str:
        return "Simulates posting to social media platforms in a sandbox environment for validation."

    @property
    def args_schema(self) -> Type[BaseModel]:
        return PostToSocialSandboxSchema

    def execute(self, **kwargs) -> str:
        platform = kwargs.get("platform")
        content = kwargs.get("content")
        subreddit = kwargs.get("subreddit")
        
        log_msg = f"[SANDBOX POST] Platform: {platform.upper()}"
        if subreddit:
            log_msg += f" | Community: r/{subreddit}"
        log_msg += f"\nContent:\n{content}\n" + "-"*30
        
        logger.info(log_msg)
        return f"Successfully 'posted' to {platform} sandbox."

class MarketingAgent(BaseAgent):
    """
    Marketing Agent: growth lead. Owns "Awareness".
    Writes ad copy, landing page copy, and social posts.
    Informed by Segment Prioritization and Product Hypotheses.
    """
    def __init__(self, name: str, event_bus: EventBus):
        super().__init__(name, event_bus)
        self.reasoning_client = ReasoningModelClient()
        self._functions = [
            GenerateCopyFunction(self.reasoning_client),
            PostToSocialSandboxFunction()
        ]

    @property
    def role(self) -> str:
        return "Growth Lead: Manages Awareness through high-impact Copy and Social Campaigning."

    @property
    def functions(self) -> List[AgentFunction]:
        return self._functions

    def setup_subscriptions(self):
        # Subscribe to PRD completion to automatically start marketing awareness
        self.event_bus.subscribe("PRD_COMPLETED", self.on_prd_completed)
        self.event_bus.subscribe("MARKETING_CAMPAIGN_REQUESTED", self.run_campaign_workflow)

    def on_prd_completed(self, payload: Any):
        logger.info(f"Marketing Agent: Blueprint (PRD) received for {payload.get('project_name')}. Crafting awareness strategy...")
        self.run_campaign_workflow(payload)

    def run_campaign_workflow(self, context: Dict[str, Any]):
        industry = context.get("industry", "General")
        segment = context.get("segment", "Target Segment")
        project_name = context.get("project_name", "New Project")
        prd_content = context.get("prd_content", "")

        logger.info(f"Marketing Agent: Starting 'Growth Engine' for {project_name} in {industry}...")

        # 1. Look at #1 customer segment in segment_prioritization.md to understand Segment Profile
        segment_profile = self._get_segment_profile(industry, segment)
        
        # 2. Extract Value Proposition from product documents
        value_prop = self._extract_value_prop(prd_content if prd_content else project_name)

        # 3. Generate Ad and Landing Page Copy
        logger.info("Marketing Agent: Generating Ad Copy and Landing Page content...")
        ad_copy = self._generate_ad_copy(project_name, segment_profile, value_prop)
        
        # 4. Generate Social Media Posts (Reddit, X)
        logger.info("Marketing Agent: Generating viral Social Media content...")
        social_posts = self._generate_social_posts(project_name, segment_profile, value_prop)

        # 5. Configure Ad Targeting
        logger.info("Marketing Agent: Designing precision targeting parameters...")
        targeting = self._configure_targeting(segment_profile)

        # 6. Persist Marketing Portfolio
        output_paths = self._persist_marketing_materials(industry, segment, project_name, {
            "ad_copy": ad_copy,
            "social_posts": social_posts,
            "targeting": targeting,
            "value_prop": value_prop
        })

        # 7. Notify completion
        self.publish_event("MARKETING_COMPLETED", {
            "project_name": project_name,
            "saved_paths": output_paths,
            "summary": "Full awareness suite generated (Ads, Landing Page, Social Posts, Targeting)."
        })

    def _get_segment_profile(self, industry: str, segment: str) -> str:
        """
        Reads segment_prioritization.md to understand the profile of the #1 prioritied segment.
        """
        safe_industry = industry.replace(" ", "_").lower()
        prioritization_file = os.path.join("output", safe_industry, "market_landscape", "segment_prioritization.md")
        
        if os.path.exists(prioritization_file):
            try:
                with open(prioritization_file, "r") as f:
                    content = f.read()
                    # Heuristically find the top segment analysis section
                    if "### **Top Segment Analysis**" in content:
                        analysis = content.split("### **Top Segment Analysis**")[-1].split("---")[0].strip()
                        return analysis
                    return content[:2000] # Fallback
            except Exception as e:
                logger.error(f"Error reading segment priority: {e}")
        
        return f"Targeting Segment: {segment}"

    def _extract_value_prop(self, context: str) -> str:
        prompt = f"Analyze this context and distill the ONE 'insanely great' value proposition that will change the market:\n\n{context[:3000]}"
        return self.reasoning_client.generate(prompt, system_prompt="You are Steve Jobs meeting a visionary founder.")

    def _generate_ad_copy(self, project: str, segment_profile: str, value_prop: str) -> str:
        prompt = f"""
        Craft a marketing suite for '{project}'.
        
        Target Segment Context:
        {segment_profile}
        
        Core Value Proposition:
        {value_prop}
        
        Generate:
        1. An 'Apple-style' landing page headline and hero copy (Minimalist, aspirational).
        2. A high-conversion Google Search Ad (Headlines & Descriptions).
        3. A disruptive Facebook/Instagram Ad hook.
        """
        return self.functions[0].execute(prompt=prompt, tone="bold", platform="landing_page")

    def _generate_social_posts(self, project: str, segment_profile: str, value_prop: str) -> Dict[str, str]:
        # X Thread
        x_prompt = f"Write a 4-post X (Twitter) thread launching {project}. Start with a disruptive hook that stops the scroll. Value prop: {value_prop}."
        x_post = self.functions[0].execute(prompt=x_prompt, tone="provocative", platform="twitter")
        
        # Reddit Post
        reddit_prompt = f"Write a long-form Reddit post for a relevant niche community about {project}. Don't sell; provide immense value and bridge it to {project}. Value prop: {value_prop}."
        reddit_post = self.functions[0].execute(prompt=reddit_prompt, tone="intellectual", platform="reddit")
        
        return {"x": x_post, "reddit": reddit_post}

    def _configure_targeting(self, segment_profile: str) -> str:
        prompt = f"Translate this segment profile into technical ad targeting parameters (Interests, Demographics, Job Titles, Behaviors) for LinkedIn and Meta Ads:\n\n{segment_profile}"
        return self.reasoning_client.generate(prompt, system_prompt="You are Elon Musk optimizing a launch for maximum signal-to-noise ratio.")

    def _persist_marketing_materials(self, industry: str, segment: str, project: str, materials: Dict[str, Any]) -> Dict[str, str]:
        safe_industry = industry.replace(" ", "_").lower()
        safe_segment = segment.replace(" ", "_").lower()
        safe_project = project.replace(" ", "_").lower().replace("/", "_")
        
        # Consistent output structure: output/[industry]/[segment]/marketing/[project]/
        out_dir = os.path.join("output", safe_industry, safe_segment, "marketing", safe_project)
        os.makedirs(out_dir, exist_ok=True)
        
        strat_file = os.path.join(out_dir, "awareness_campaign.md")
        with open(strat_file, "w") as f:
            f.write(f"# Growth Campaign: {project}\n\n")
            f.write(f"## 1. Master Value Proposition\n{materials['value_prop']}\n\n")
            f.write(f"## 2. Ad & Landing Page Suite\n{materials['ad_copy']}\n\n")
            f.write(f"## 3. Social Presence\n")
            f.write(f"### X Thread\n{materials['social_posts']['x']}\n\n")
            f.write(f"### Reddit Strategy\n{materials['social_posts']['reddit']}\n\n")
            f.write(f"## 4. Precision Targeting Matrix\n{materials['targeting']}\n")
            
        logger.info(f"Marketing Agent: Awareness assets deployed to {out_dir}")
        return {"campaign_doc": strat_file}
