"""Content planning agent."""
import json
from .client import QwenClient


SYSTEM_PROMPT = """You are an educational content planner. Given a topic, create a structured learning plan with 3-4 segments. For each segment output:
- segment_id: number (1, 2, 3, 4)
- title: short title
- concept: what to explain
- visual_type: one of (text, equation, diagram)
- script: 2-3 sentence narration

Return ONLY valid JSON array, no markdown code blocks, no explanations, no extra text."""


async def plan_lesson(client: QwenClient, topic: str) -> list[dict]:
    """Generate lesson plan for topic."""
    response = await client.call(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=f"Plan a lesson about {topic}",
        model="qwen-flash",
        temperature=0.7,
        response_format={"type": "json_object"},
    )
    
    # Clean markdown artifacts
    response = response.strip().strip("`")
    if response.startswith("```"):
        response = response.split("```")[1]
        if response.startswith("json"):
            response = response[4:]
    response = response.strip()
    
    result = json.loads(response)
    # Handle wrapped responses
    if isinstance(result, dict) and "segments" in result:
        return result["segments"]
    if isinstance(result, dict) and "plan" in result:
        return result["plan"]
    return result
