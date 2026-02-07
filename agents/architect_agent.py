import os
import logging
import subprocess
from typing import Any, Dict, List
from core.base_agent import BaseAgent, AgentFunction
from infrastructure.llm.reasoning_model_client import ReasoningModelClient
from infrastructure.event_bus import EventBus

logger = logging.getLogger(__name__)

class ArchitectAgent(BaseAgent):
    """
    Architect Agent: Owns the 'Structure' & 'Plan'.
    """
    def __init__(self, name: str, event_bus: EventBus):
        super().__init__(name, event_bus)
        self.reasoning_client = ReasoningModelClient()

    @property
    def role(self) -> str:
        return "Software Architect: Designs high-level system structures, schemas, and API specs."

    @property
    def functions(self) -> List[AgentFunction]:
        return []

    def setup_subscriptions(self):
        # Subscribe to PRD completion events
        self.event_bus.subscribe("PRD_COMPLETED", self.on_prd_completed)

    def handle_instruction(self, instruction: str, context: Dict[str, Any]):
        """
        Handle direct instructions like 'Review this PRD and architecture it'.
        """
        if "design" in instruction.lower() or "architect" in instruction.lower():
            prd_content = context.get("prd_content")
            project_name = context.get("project_name", "NewProject")
            industry = context.get("industry")
            segment = context.get("segment")
            if prd_content:
                self._run_design_workflow(prd_content, project_name, industry, segment)
            else:
                logger.error("Architect Agent: No PRD content provided in context.")
        else:
            logger.warning(f"Architect Agent: Unknown instruction: {instruction}")

    def on_prd_completed(self, payload: Any):
        try:
            prd_content = payload.get("prd_content")
            project_name = payload.get("project_name", "Untitled")
            industry = payload.get("industry")
            segment = payload.get("segment")
            logger.info(f"Architect Agent: Received PRD for {project_name}. Starting architectural design...")
            
            self._run_design_workflow(prd_content, project_name, industry, segment)
        except Exception as e:
            logger.error(f"Architect Agent: Error in on_prd_completed: {e}", exc_info=True)

    def _run_design_workflow(self, prd_content: str, project_name: str, industry: str = None, segment: str = None):
        # 1. Define output path
        safe_project = project_name.replace(" ", "_").lower()
        if industry:
            safe_industry = industry.replace(" ", "_").lower()
            output_dir = os.path.join("output", safe_industry, "designs")
        else:
            output_dir = os.path.join("output", safe_project, "designs")

        output_path = os.path.join(output_dir, f"{safe_project}_system_design.md")
        
        # 2. Execute the tool
        design_doc = self._generate_design_doc(
            prd_content=prd_content,
            project_name=project_name,
            output_path=output_path
        )
        
        # 3. Commit to GitHub (Simulated/Local Git implementation)
        self._commit_to_git(output_path, f"Design: Core architecture for {project_name}")
        
        # 4. Publish approval event
        self.publish_event("DESIGN_DOC_COMPLETED", {
            "project_name": project_name,
            "design_doc_path": output_path,
            "architecture_summary": "Architecture, DB Schema, and API Spec defined."
        })

    def _generate_design_doc(self, prd_content: str, project_name: str, output_path: str) -> str:
        logger.info(f"Architect: Generating Design Doc for {project_name}...")
        
        prompt = f"""
        You are a Distinguished Engineer and System Architect (like Jeff Dean).
        Design a robust, scalable system based on the following PRD.

        **PRD Content:**
        {prd_content}

        **Design Doc Title Requirement:**
        The design doc must include the product idea title: "{project_name}"

        **Requirements for the Design Doc:**
        1. **Executive Summary**: High-level overview of the technical approach.
        2. **Technology Stack**: Select the best stack (Languages, Frameworks, Databases, Cloud Services) with justifications.
        3. **System Architecture**: Define the high-level components and their interactions (Context Diagram, Container Diagram).
        4. **Database Schema**: Detailed SQL or NoSQL schema (Tables, Columns, Relationships).
        5. **API Specification**: Comprehensive OpenAPI/Swagger spec or equivalent (Endpoints, Payloads, Responses).
        6. **UI Component Breakdown**: Hierarchical breakdown of frontend components.
        7. **Data Flow**: Explain how data moves through the critical paths.
        8. **Security & Scalability**: How the system handles growth and protects data.

        Format the output in professional GitHub-flavored Markdown.
        """

        try:
            design_doc = self.reasoning_client.generate(
                prompt, 
                system_prompt="You are a World-Class System Architect. You value simplicity, scalability, and performance."
            )

            if project_name not in design_doc:
                design_doc = f"# {project_name} System Design\n\n{design_doc}"

            # Save the file
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as f:
                f.write(design_doc)
            
            return design_doc
        except Exception as e:
            logger.error(f"Architect Agent: Failed to generate design doc: {e}", exc_info=True)
            raise

    def _commit_to_git(self, file_path: str, message: str):
        """
        Commits the generated design doc to the repository.
        """
        try:
            # Check if we are in a git repo
            subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, capture_output=True)
            
            # Stage and commit
            subprocess.run(["git", "add", file_path], check=True)
            subprocess.run(["git", "commit", "-m", message], check=True)
            logger.info(f"Architect Agent: Committed {file_path} to Git.")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Architect Agent: Failed to commit to Git: {e}")
        except Exception as e:
            logger.error(f"Architect Agent: Error during Git operation: {e}")
