"""Text-to-Speech generator using Edge-TTS (Free Microsoft TTS)."""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def _generate_audio_async(text: str, output_path: str, voice: str) -> dict:
    """Async helper to generate audio."""
    try:
        import edge_tts
        
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        
        return {"success": True, "audio_path": output_path, "error": None}
    except Exception as e:
        return {"success": False, "audio_path": None, "error": str(e)}


def generate_audio(text: str, output_path: str, voice: str = None) -> dict:
    """
    Generate audio from text using Edge-TTS (Free Microsoft TTS).
    
    Args:
        text: Text to convert to speech
        output_path: Path where audio file will be saved
        voice: Voice name (default: ar-EG-SalmaNeural for Egyptian Arabic)
               Other options: ar-SA-HamedNeural, ar-EG-ShakirNeural
    
    Returns:
        Dictionary with success status, audio path, and error message
    """
    try:
        import edge_tts
    except ImportError:
        return {"success": False, "audio_path": None, "error": "edge-tts not installed. Run: pip install edge-tts"}
    
    # Use voice from parameter, env, or default
    if voice is None:
        voice = os.getenv("EDGE_VOICE", "ar-EG-SalmaNeural")
    
    # Run async function synchronously
    result = asyncio.run(_generate_audio_async(text, output_path, voice))
    return result
