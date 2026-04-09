from typing import Any, Dict, List, Type
import logging
import os
import json
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
        return "Generates high-converting marketing copy for various platforms."

    @property
    def args_schema(self) -> Type[BaseModel]:
        return GenerateCopySchema

    def execute(self, **kwargs) -> str:
        prompt = kwargs.get("prompt")
        tone = kwargs.get("tone")
        platform = kwargs.get("platform")
        
        system_prompt = (
            f"You are a world-class growth marketer with the strategic vision of Steve Jobs "
            f"and the disruptive energy of Elon Musk. Focus on 'Awareness'. Tone: {tone}. Platform: {platform}."
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
        return "Simulates posting to social media platforms in a sandbox environment."

    @property
    def args_schema(self) -> Type[BaseModel]:
        return PostToSocialSandboxSchema

    def execute(self, **kwargs) -> str:
        platform = kwargs.get("platform")
        content = kwargs.get("content")
        subreddit = kwargs.get("subreddit")
        
        log_msg = f"[SANDBOX Post] Platform: {platform.upper()}"
        if subreddit: log_msg += f" (r/{subreddit})"
        log_msg += f"\nContent:\n{content}\n" + "-"*30
        
        logger.info(log_msg)
        return f"Successfully 'posted' to {platform} sandbox."

class MarketingAgent(BaseAgent):
    """
    Marketing Agent: growth lead. Owns "Awareness".
    Stage 1: Generate Marketing Plan -> Review -> Approval.
    Stage 2: Generate Copy, Posts, and Targeting.
    """
    def __init__(self, name: str, event_bus: EventBus):
        super().__init__(name, event_bus)
        self.reasoning_client = ReasoningModelClient()
        self._functions = [
            GenerateCopyFunction(self.reasoning_client),
            PostToSocialSandboxFunction()
        ]
        # In-memory session state for pending approvals
        self._pending_campaigns: Dict[str, Dict[str, Any]] = {}

    @property
    def role(self) -> str:
        return "Growth Lead: Manages awareness through strategic planning and high-impact content."

    @property
    def functions(self) -> List[AgentFunction]:
        return self._functions

    def setup_subscriptions(self):
        self.event_bus.subscribe("PRD_COMPLETED", self.on_prd_completed)
        self.event_bus.subscribe("MARKETING_CAMPAIGN_REQUESTED", self.run_campaign_workflow)
        self.event_bus.subscribe("MARKETING_PLAN_APPROVED", self.on_marketing_plan_approved)

    def on_prd_completed(self, payload: Any):
        logger.info(f"Marketing Agent: Blueprint (PRD) detected for {payload.get('project_name')}.")
        self.run_campaign_workflow(payload)

    def run_campaign_workflow(self, context: Dict[str, Any]):
        """
        Stage 1: Preparation and Planning.
        """
        target_industry = context.get("target_industry") or context.get("industry") or "athletes"
        project_name = context.get("project_name", "New Project")
        segment = context.get("segment", "General")

        logger.info(f"Marketing Agent: Initiating Stage 1 Planning for {project_name} in '{target_industry}' industry...")

        # 1. Load context from output/{industry}/product/
        product_context = self._load_product_context(target_industry)
        
        # 2. Get Segment Profile from prioritization
        segment_profile = self._get_segment_profile(target_industry, segment)
        
        # 3. Generate high-level value prop
        value_prop = self._extract_value_prop(product_context if product_context else project_name)

        # 4. Generate the Marketing Plan (User vs Agent tasks)
        logger.info("Marketing Agent: Crafting Marketing Plan for user review...")
        plan_content = self._generate_marketing_plan(project_name, target_industry, segment_profile, value_prop)

        # 5. Persist the plan
        output_dir = os.path.join("output", target_industry.replace(" ", "_").lower(), "marketing")
        os.makedirs(output_dir, exist_ok=True)
        plan_path = os.path.join(output_dir, f"marketing_plan_{project_name.lower().replace(' ', '_')}.md")
        with open(plan_path, "w") as f:
            f.write(plan_content)

        # 6. Store context for Stage 2
        campaign_id = f"{target_industry}_{project_name}".replace(" ", "_").lower()
        self._pending_campaigns[campaign_id] = {
            "industry": target_industry,
            "project_name": project_name,
            "segment_profile": segment_profile,
            "value_prop": value_prop,
            "output_dir": output_dir
        }

        logger.info(f"Marketing Agent: Stage 1 COMPLETE. Plan available at: {plan_path}")
        self.publish_event("MARKETING_PLAN_GENERATED", {
            "campaign_id": campaign_id,
            "plan_path": plan_path,
            "project_name": project_name
        })

    def on_marketing_plan_approved(self, payload: Dict[str, Any]):
        """
        Stage 2: Execution after user approval.
        """
        campaign_id = payload.get("campaign_id")
        if not campaign_id or campaign_id not in self._pending_campaigns:
            logger.error(f"Marketing Agent: Cannot approve unknown campaign ID: {campaign_id}")
            return

        context = self._pending_campaigns.pop(campaign_id)
        logger.info(f"Marketing Agent: Approval received for {context['project_name']}. Executing Stage 2...")
        self._execute_campaign_execution(context)

    def _execute_campaign_execution(self, context: Dict[str, Any]):
        project_name = context["project_name"]
        segment_profile = context["segment_profile"]
        value_prop = context["value_prop"]
        output_dir = context["output_dir"]
        industry = context["industry"]

        # 1. Generate Ad/Landing Copy
        logger.info("Marketing Agent: Generating Ad Copy and Landing Page assets...")
        ad_copy = self._generate_ad_copy(project_name, segment_profile, value_prop)
        
        # 2. Generate Social Posts
        logger.info("Marketing Agent: Generating Social Media posts...")
        social_posts = self._generate_social_posts(project_name, segment_profile, value_prop)

        # 3. Configure Targeting
        logger.info("Marketing Agent: Configuring ad targeting parameters...")
        targeting = self._configure_targeting(segment_profile)

        # 4. Save Final Assets
        project_slug = project_name.replace(" ", "_").lower()
        assets_dir = os.path.join(output_dir, project_slug)
        os.makedirs(assets_dir, exist_ok=True)
        
        assets_file = os.path.join(assets_dir, "campaign_assets.md")
        with open(assets_file, "w") as f:
            f.write(f"# Marketing Campaign Assets: {project_name}\n\n")
            f.write(f"## Ad Copy & Landing Page\n{ad_copy}\n\n")
            f.write(f"## Social Posts\n### X\n{social_posts['x']}\n\n### Reddit\n{social_posts['reddit']}\n\n")
            f.write(f"## Ad Targeting\n{targeting}\n")

        logger.info(f"Marketing Agent: Stage 2 COMPLETE. Assets saved to {assets_dir}")
        self.publish_event("MARKETING_COMPLETED", {
            "project_name": project_name,
            "assets_path": assets_file
        })

    def _load_product_context(self, industry: str) -> str:
        safe_industry = industry.replace(" ", "_").lower()
        product_dir = os.path.join("output", safe_industry, "product")
        if not os.path.exists(product_dir):
            return ""
        
        context_parts = []
        for file in os.listdir(product_dir):
            if file.endswith(".md"):
                try:
                    with open(os.path.join(product_dir, file), "r") as f:
                        context_parts.append(f.read())
                except Exception as e:
                    logger.error(f"Error reading product context file {file}: {e}")
        return "\n\n".join(context_parts)

    def _get_segment_profile(self, industry: str, segment: str) -> str:
        safe_industry = industry.replace(" ", "_").lower()
        prioritization_file = os.path.join("output", safe_industry, "market_landscape", "segment_prioritization.md")
        if os.path.exists(prioritization_file):
            try:
                with open(prioritization_file, "r") as f:
                    content = f.read()
                    if "### **Top Segment Analysis**" in content:
                        return content.split("### **Top Segment Analysis**")[-1].split("---")[0].strip()
                    return content[:2000]
            except Exception as e:
                logger.error(f"Error reading segment prioritization: {e}")
        return f"Target Segment: {segment}"

    def _extract_value_prop(self, context: str) -> str:
        prompt = f"Extract a world-class, 'insanely great' value proposition from these product details:\n\n{context[:4000]}"
        return self.reasoning_client.generate(prompt, system_prompt="You are Steve Jobs meeting his lead engineers.")

    def _generate_marketing_plan(self, project: str, industry: str, segment_profile: str, value_prop: str) -> str:
        prompt = f"""
        Compose a world-class, professionally structured Marketing Plan for '{project}' in the '{industry}' industry.
        Your goal is to WOW the user with clarity and strategic depth.
        
        **Segment Profile:**
        {segment_profile}
        
        **Core Value Prop:**
        {value_prop}
        
        The plan MUST be formatted in clean Markdown with the following sections:
        
        ### 1. Executive Summary
        A punchy, 3-sentence summary of why this campaign will disrupt the '{industry}' market.
        
        ### 2. Strategic Direction & 'North Star'
        Channel the vision of Steve Jobs. What is the fundamental change we are bringing to the world?
        
        ### 3. Multi-Channel Execution Strategy
        Detail how we will dominate X (Twitter), Reddit, and Search Ads.
        
        ### 4. 🛑 USER ACTIONS (Required for Approval)
        Clearly list the specific decisions and inputs required from the Human User to proceed. Use a table or bolded list.
        Examples: Budget caps, Tone validation, Specific community targets, Legal check-off.
        
        ### 5. 🤖 AGENT TASKS (Automated on Approval)
        Explain what the Marketing Agent will handle with precision once approved.
        Examples: High-conversion copywriting, Ad targeting configuration, Social hook generation, Sandbox validation.
        
        Use professional, impactful language throughout.
        """
        return self.reasoning_client.generate(prompt, system_prompt="You are an Elite Growth Strategist with the vision of Jobs and the speed of Musk. Your output should be visually striking and perfectly organized.")

    def _generate_ad_copy(self, project: str, segment_profile: str, value_prop: str) -> str:
        prompt = f"Craft an 'Apple-style' landing page headline and a high-conversion Google Search Ad for {project}.\nVP: {value_prop}\nAudience: {segment_profile[:500]}"
        return self.functions[0].execute(prompt=prompt, tone="bold", platform="landing_page")

    def _generate_social_posts(self, project: str, segment_profile: str, value_prop: str) -> Dict[str, str]:
        x_post = self.functions[0].execute(prompt=f"Viral X hook for {project}. VP: {value_prop}", tone="provocative", platform="twitter")
        reddit_post = self.functions[0].execute(prompt=f"Value-first Reddit post for {project}. VP: {value_prop}", tone="intellectual", platform="reddit")
        return {"x": x_post, "reddit": reddit_post}

    def _configure_targeting(self, segment_profile: str) -> str:
        prompt = f"Define precision ad targeting for LinkedIn and Meta based on this profile: {segment_profile}"
        return self.reasoning_client.generate(prompt, system_prompt="You are Elon Musk optimizing a launch for signal-to-noise ratio.")
