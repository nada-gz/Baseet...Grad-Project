"""Text-to-Speech generator using ElevenLabs API."""
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os

load_dotenv()


def generate_audio(text: str, output_path: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb") -> dict:
    """
    Generate audio from text using ElevenLabs API with slower, clearer speech.
    
    Args:
        text: Text to convert to speech
        output_path: Path where audio file will be saved
        voice_id: Voice ID (default: "JBFqnCBsd6RMkjVDRZzb" - Rachel-like voice)
                  Get voice IDs from: client.voices.search() or https://elevenlabs.io/app/voice-lab
    
    Returns:
        Dictionary with success status, audio path, and error message
    """
    try:
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            return {"success": False, "audio_path": None, "error": "ELEVENLABS_API_KEY not found in .env"}
        
        client = ElevenLabs(api_key=api_key)
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            voice_settings={
                "stability": 0.75,        # Higher stability for clearer speech
                "similarity_boost": 0.8,  # Maintain voice consistency
                "style": 0.0,            # No exaggerated emotion
                "use_speaker_boost": True
            }
        )
        
        # Consume the generator and write audio bytes
        with open(output_path, "wb") as f:
            for chunk in audio_generator:
                f.write(chunk)
        
        return {"success": True, "audio_path": output_path, "error": None}
    except Exception as e:
        return {"success": False, "audio_path": None, "error": str(e)}
