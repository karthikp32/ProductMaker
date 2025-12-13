import os
import logging
import requests
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)

class LLMJudge:
    """
    Evaluates content using DeepSeek R1 via OpenRouter.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_DEEPSEEK_R1_API_KEY")
        if not self.api_key:
            logger.warning("OPENROUTER_DEEPSEEK_R1_API_KEY not found. Judge will fail.")
        
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

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
        4. **Acquisition Channels:** Does it mention where these people hang out and can be acquired (Subreddits, Forums, etc.)?
        5. **Willingness to Pay:** Is there any data on pricing?

        **Output Format:**
        Provide a JSON response with the following keys:
        - score (1-10)
        - reasoning (brief explanation)
        - missing_elements (list of what's missing)
        """

        try:
            response = requests.post(
                url=self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000", 
                    "X-Title": "ProductMaker Judge", 
                },
                data=json.dumps({
                    "model": "deepseek/deepseek-r1:free", # Using free alias or exact model if known
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a strict evaluator of market research reports. Return ONLY valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "response_format": { "type": "json_object" }
                })
            )
            
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Attempt to parse JSON if model returned stringified JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"score": 0, "reasoning": "Failed to parse JSON output", "raw_output": content}

        except Exception as e:
            logger.error(f"LLM Judge Evaluation failed: {e}")
            return {"error": str(e)}
