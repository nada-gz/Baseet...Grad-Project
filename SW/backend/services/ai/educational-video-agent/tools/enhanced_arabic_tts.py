"""
Enhanced Arabic TTS with ElevenLabs (primary) and Edge-TTS (fallback).
Uses Egyptian dialect processing for natural speech.
"""
import os
import asyncio
import base64
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Import ElevenLabs
try:
    from elevenlabs import VoiceSettings
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    print("⚠️  ElevenLabs not installed. Will use Edge-TTS only.")

# Import Edge-TTS
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    print("⚠️  Edge-TTS not installed. Will use ElevenLabs only.")


class ElevenLabsTTS:
    """ElevenLabs TTS with Egyptian dialect support."""
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
        self.client = None
        
        if ELEVENLABS_AVAILABLE and self.api_key:
            try:
                self.client = ElevenLabs(api_key=self.api_key)
                print(f"✅ ElevenLabs TTS initialized (Voice: {self.voice_id})")
            except Exception as e:
                print(f"❌ ElevenLabs init failed: {e}")
    
    async def generate_audio_async(self, text: str, output_path: str) -> dict:
        """Generate audio using ElevenLabs."""
        if not self.client:
            return {"success": False, "error": "ElevenLabs not available"}
        
        try:
            print(f"  🎤 ElevenLabs: Generating audio...")
            
            # Generate audio
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id="eleven_multilingual_v2",
                voice_settings=VoiceSettings(
                    stability=0.90,
                    similarity_boost=0.50,
                    style=0.0,
                    use_speaker_boost=True
                )
            )
            
            # Collect audio bytes
            audio_bytes = b"".join(audio_generator)
            
            # Save to file
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            
            return {
                "success": True,
                "audio_path": output_path,
                "error": None,
                "provider": "ElevenLabs"
            }
            
        except Exception as e:
            return {
                "success": False,
                "audio_path": None,
                "error": str(e),
                "provider": "ElevenLabs"
            }


class EdgeTTSFallback:
    """Edge-TTS fallback with Standard Arabic."""
    
    def __init__(self):
        self.voice = os.getenv("EDGE_VOICE", "ar-SA-ZariyahNeural")
        print(f"✅ Edge-TTS fallback ready (Voice: {self.voice})")
    
    async def generate_audio_async(self, text: str, output_path: str) -> dict:
        """Generate audio using Edge-TTS."""
        if not EDGE_TTS_AVAILABLE:
            return {"success": False, "error": "Edge-TTS not available"}
        
        try:
            print(f"  🎤 Edge-TTS (fallback): Generating audio...")
            
            # Generate audio
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_path)
            
            return {
                "success": True,
                "audio_path": output_path,
                "error": None,
                "provider": "Edge-TTS"
            }
            
        except Exception as e:
            return {
                "success": False,
                "audio_path": None,
                "error": str(e),
                "provider": "Edge-TTS"
            }


class EnhancedArabicTTS:
    """
    Enhanced Arabic TTS with automatic fallback.
    Primary: ElevenLabs (better quality, Egyptian dialect)
    Fallback: Edge-TTS (free, Standard Arabic)
    """
    
    def __init__(self):
        self.elevenlabs = ElevenLabsTTS()
        self.edge_tts = EdgeTTSFallback()
    
    async def generate_arabic_audio_async(self, arabic_text: str, output_path: str) -> dict:
        """
        Generate Arabic audio with automatic fallback.
        
        Args:
            arabic_text: Arabic text to narrate
            output_path: Where to save the MP3 file
            
        Returns:
            dict with success, audio_path, error, provider
        """
        print(f"  ✨ Text: {arabic_text[:80]}...")
        
        # Try ElevenLabs first
        if self.elevenlabs.client:
            result = await self.elevenlabs.generate_audio_async(arabic_text, output_path)
            if result["success"]:
                print(f"  ✅ Audio generated via {result['provider']}")
                return result
            else:
                print(f"  ⚠️  ElevenLabs failed: {result['error']}")
                print(f"  🔄 Falling back to Edge-TTS...")
        
        # Fallback to Edge-TTS
        result = await self.edge_tts.generate_audio_async(arabic_text, output_path)
        if result["success"]:
            print(f"  ✅ Audio generated via {result['provider']}")
        else:
            print(f"  ❌ Both TTS providers failed!")
        
        return result


# Singleton instance
_tts_instance = None

def get_enhanced_arabic_tts() -> EnhancedArabicTTS:
    """Get or create enhanced TTS singleton."""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = EnhancedArabicTTS()
    return _tts_instance


async def generate_arabic_narration_async(arabic_text: str, output_path: str) -> dict:
    """
    Generate Arabic audio with automatic fallback.
    
    Args:
        arabic_text: Text in Arabic to narrate
        output_path: Path to save the MP3 file
        
    Returns:
        dict with success, audio_path, error, provider
    """
    tts = get_enhanced_arabic_tts()
    return await tts.generate_arabic_audio_async(arabic_text, output_path)


if __name__ == "__main__":
    # Test
    async def test():
        result = await generate_arabic_narration_async(
            "مرحباً، هذا اختبار للنظام الصوتي المحسّن",
            "test_enhanced_tts.mp3"
        )
        print(f"\nResult: {result}")
    
    asyncio.run(test())
