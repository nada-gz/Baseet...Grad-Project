"""Content planning agent."""
import json
from .client import QwenClient


def get_system_prompt(num_segments: int) -> str:
    """Generate system prompt based on desired number of segments."""
    return f"""You are an educational content planner. Given a topic, create a structured learning plan with exactly {num_segments} segments. For each segment output:
- segment_id: number (1, 2, 3, ... {num_segments})
- title: short title
- concept: what to explain in detail
- visual_type: one of (text, equation, diagram, animation)
- script: 3-4 sentence detailed narration that takes about 15 seconds to read

IMPORTANT: Create exactly {num_segments} segments, each with a meaningful educational concept.
Return ONLY valid JSON array, no markdown code blocks, no explanations, no extra text."""


async def plan_lesson(client: QwenClient, topic: str, target_duration_minutes: float = 1.0) -> list[dict]:
    """
    Generate lesson plan for topic.
    
    Args:
        client: QwenClient instance
        topic: Educational topic
        target_duration_minutes: Target video duration in minutes
        
    Returns:
        List of segment dictionaries
    """
    # Calculate number of segments: ~15 seconds per segment audio
    # So for 1 minute we need 4 segments, for 2 minutes we need 8, etc.
    num_segments = max(4, int(target_duration_minutes * 4))
    
    system_prompt = get_system_prompt(num_segments)
    
    response = await client.call(
        system_prompt=system_prompt,
        user_prompt=f"Plan a comprehensive lesson about {topic}. Make sure to cover {num_segments} different aspects or concepts.",
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
