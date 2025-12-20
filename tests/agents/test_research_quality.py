import unittest
import os
import logging
from agents.pm_agent import PMAgent
from infrastructure.event_bus import EventBus
from tests.utils.llm_judge import LLMJudge

# Configure logging to see output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DeepResearchEvaluation")

class TestDeepResearchQuality(unittest.TestCase):
    """
    Integration test that runs valid Deep Research and uses LLM Judge to score it.
    REQUIRES: GEMINI_API_KEY and OPENROUTER_DEEPSEEK_R1_API_KEY
    """
    
    def setUp(self):
        # We need the real keys for this test
        if not os.getenv("GEMINI_API_KEY") or not os.getenv("OPENROUTER_DEEPSEEK_R1_API_KEY"):
            self.skipTest("Skipping DeepResearch Quality test: Missing API Keys")
            
        self.bus = EventBus()
        self.agent = PMAgent("PMAgent", self.bus)
        self.judge = LLMJudge()

    def test_research_quality_indie_devs(self):
        topic = "Indie Game Developers"
        
        logger.info(f"--- Starting Deep Research on: {topic} ---")
        
        # 1. Run the real Deep Research (via PMAgent)
        research_output = self.agent.research_customer_segment(topic)
        
        # 2. Save output to file for manual inspection
        output_file = f"tests/agents/research_output_{topic.replace(' ', '_')}.txt"
        with open(output_file, "w") as f:
            f.write(research_output)
        logger.info(f"Research output saved to: {output_file}")
        
        # 3. Evaluate with LLM Judge
        logger.info("--- Evaluating with DeepSeek R1 Judge ---")
        evaluation = self.judge.evaluate_research(topic, research_output)
        
        logger.info(f"Judge Score: {evaluation.get('score')}")
        logger.info(f"Judge Reasoning: {evaluation.get('reasoning')}")
        
        # 4. Assertions (Quality Gate)
        # Check if score is decent (e.g. > 6/10)
        score = evaluation.get("score", 0)
        self.assertGreaterEqual(score, 6, f"Research quality too low: {evaluation.get('reasoning')}")

if __name__ == '__main__':
    unittest.main()
