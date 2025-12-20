import os
import logging
import json
from typing import Dict, Any
from litellm import completion

logger = logging.getLogger(__name__)

class LLMJudge:
    """
    Evaluates content using DeepSeek R1 via OpenRouter (using litellm).
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_DEEPSEEK_R1_API_KEY")
        if not self.api_key:
            logger.warning("OPENROUTER_DEEPSEEK_R1_API_KEY not found. Judge will fail.")
        
    def evaluate_research(self, topic: str, research_content: str) -> Dict[str, Any]:
        """
        Asks DeepSeek R1 to evaluate the quality of the market research.
        """
        prompt = f"""
        You are an expert impartial judge evaluating the quality of AI-generated Market Research.

        **Topic:** {topic}

        **Research Content to Evaluate:**
        {research_content}

        **Evaluation Criteria:**
        1. **Persona Detail:** Does it identify specific job titles and profiles?
        2. **Pain Points:** Are the pain points specific and actionable?
        3. **Existing Solutions:** Does it mention real competitors or solution types?
        4. **Acquisition Channels:** Does it mention where these people hang out (Reddit, Forums)?
        5. **Willingness to Pay:** Is there any data on pricing?

        **Output Format:**
        Provide a JSON response with the following keys:
        - score (integer 1-10)
        - reasoning (brief explanation)
        - missing_elements (list of what's missing)
        """

        try:
            logger.info("LLM Judge: Sending request to DeepSeek R1 via OpenRouter...")
            response = completion(
                model="openrouter/deepseek/deepseek-r1-0528:free",
                messages=[
                    {"role": "system", "content": "You are a strict evaluator. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                api_key=self.api_key,
                response_format={ "type": "json_object" }
            )
            
            content = response.choices[0].message.content
            
            # Attempt to parse JSON
            try:
                # Handle cases where the model might wrap JSON in backticks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                return json.loads(content)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from judge: {content}")
                return {"score": 0, "reasoning": "Failed to parse JSON output", "raw_output": content}

        except Exception as e:
            logger.error(f"LLM Judge Evaluation failed: {e}")
            return {"error": str(e), "score": 0}
