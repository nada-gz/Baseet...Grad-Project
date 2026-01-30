"""
Arabic TTS Wrapper - Using Edge-TTS (Free Microsoft TTS).
Generates Arabic audio for educational video content.
"""
import os
import sys
import re
import base64
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Egyptian Arabic text processor - Enhanced version with comprehensive tashkeel
class TextPostProcessor:
    """
    Enhanced Text Normalization and Dialect Adaptation for Egyptian Arabic.
    Adds comprehensive tashkeel (diacritics) to make TTS sound more naturally Egyptian.
    """
    def __init__(self):
        # MSA to Egyptian Arabic conversions with full tashkeel
        self.msa_to_egy = {
            # Greetings and common phrases
            r"\bمرحبا\b": "مَرْحَباً",
            r"\bأهلا\b": "أَهْلاً",
            r"\bحبيبي\b": "حَبِيبِي",
            r"\bعامل ايه\b": "عَامِل إِيه",
            r"\bيا بطل\b": "يَا بَطَل",
            r"\bيا شطورة\b": "يَا شَطُّورَه",
            
            # Pronouns with tashkeel
            r"\bانت\b": "إِنْتِ",
            r"\bأنت\b": "إِنْتَ",
            r"\bانتَ\b": "إِنْتَا",
            r"\bانتا\b": "إِنْتَا",
            r"\bانتي\b": "إِنْتِي",
            r"\bهو\b": "هُوَّ",
            r"\bهي\b": "هِيَّ",
            r"\bنحن\b": "إِحْنَا",
            r"\bأنا\b": "أَنَا",
            r"\bانا\b": "أَنَا",
            
            # Questions and interrogatives
            r"\bاي الاخبار\b": "إِيه الأَخْبَار",
            r"\bايه الاخبار\b": "إِيه الأَخْبَار",
            r"\bما الاخبار\b": "إِيه الأَخْبَار",
            r"\bكيف حالك\b": "إِزَّيِّك",
            r"\bكيفك\b": "إِزَّيِّك",
            r"\bازيك\b": "إِزَّيِّك",
            r"\bإزيك\b": "إِزَّيِّك",
            r"\bكيف\b": "إِزَّاي",
            r"\bماذا\b": "إِيه",
            r"\bلماذا\b": "لِيه",
            r"\bأين\b": "فِين",
            r"\bمتى\b": "إِمْتَى",
            r"\bمن\b": "مِين",
            
            # Nature and objects
            r"\bالنباتات الخضراء\b": "النَّبَاتَات الخَضْرَا",
            r"\bالنباتات الخضرا\b": "النَّبَاتَات الخَضْرَا",
            r"\bنباتات\b": "نَبَاتَات",
            r"\bالحديقة\b": "الجِنِينَة", 
            r"\bالجنينة\b": "الجِنِينَة",
            r"\bجنينة\b": "جِنِينَة",
            r"\bالماء\b": "المَيَّة", 
            r"\bمياه\b": "مَيَّة",
            r"\bماء\b": "مَيَّة",
            r"\bالشمس\b": "الشَّمْس",
            r"\bالقمر\b": "القَمَر",
            
            # J sound words (Egyptian pronunciation)
            r"\bجميل\b": "جَمِيل",
            r"\bجديد\b": "جِدِيد",
            r"\bجاهز\b": "جَاهِز",
            r"\bجيد\b": "جَيِّد",
            
            # Common verbs
            r"\bأريد\b": "عَايِز", 
            r"\bتريد\b": "عَايِز",
            r"\bنريد\b": "عَايزِين",
            r"\bأحب\b": "بَحِب",
            r"\bأعرف\b": "أَعْرَف",
            r"\bأفهم\b": "أَفْهَم",
            r"\bقولي\b": "قُولِي",
            r"\bقلي\b": "قُولِّي",
            r"\bتعال\b": "تَعَالَى",
            r"\bاذهب\b": "رُوح",
            
            # Time and place
            r"\bالآن\b": "دِلْوَقْتِ", 
            r"\bالان\b": "دِلْوَقْتِ",
            r"\bغدا\b": "بُكْرَة",
            r"\bاليوم\b": "النَّهَارْدَة",
            r"\bأمس\b": "إِمْبَارِح",
            
            # Adjectives and descriptions  
            r"\bجدا\b": "أَوِي",
            r"\bكثير\b": "كْتِير",
            r"\bقليل\b": "شْوَيَّة",
            r"\bكبير\b": "كْبِير",
            r"\bصغير\b": "صُغَيَّر",
            r"\bجيد\b": "تَمَام",
            r"\bممتاز\b": "تَمَام أَوِي",
            
            # Demonstratives
            r"\bهذا\b": "دَا", 
            r"\bهذه\b": "دِي", 
            r"\bذلك\b": "دَاك",
            r"\bتلك\b": "دِيك",
            
            # Responses and confirmations
            r"\bنعم\b": "أَيْوَة",
            r"\bلا\b": "لَأ",
            r"\bحسنا\b": "مَاشِي",
            r"\bطيب\b": "طَيِّب",
            r"\bشكرا\b": "شُكْراً",
            r"\bمن فضلك\b": "مِن فَضْلَك",
            
            # Prepositions and particles
            r"\bسوف\b": "هَـ",
            r"\bفي\b": "فِي",
            r"\bمن\b": "مِن",
            r"\bإلى\b": "لِـ",
            r"\bعلى\b": "عَلَى",
            r"\bمع\b": "مَع",
            r"\bعن\b": "عَن",
            
            # Common words with tashkeel
            r"\bمسجد\b": "الجَامِع",
            r"\bصديقي\b": "صَاحْبِي",
            r"\bالبيت\b": "البِيت",
            r"\bالمدرسة\b": "المَدْرَسَة",
            r"\bالعمل\b": "الشُّغْل",
            r"\bالطعام\b": "الأَكْل",
        }
        
        # Enhanced diacritics dictionary for common Egyptian words
        self.egy_diacritics = {
            # Pronouns
            "انا": "أَنَا", "احنا": "إِحْنَا", "هو": "هُوَّ", "هي": "هِيَّ",
            "انت": "إِنْتَ", "انتي": "إِنْتِي",
            
            # Demonstratives
            "ده": "دَا", "دا": "دَا", "دي": "دِي", "دول": "دُول",
            
            # Common words
            "عشان": "عَشَان", "كده": "كِدَه", "كدا": "كِدَا",
            "ايه": "إِيه", "ليه": "لِيه", "ازاي": "إِزَّاي",
            "فين": "فِين", "امتى": "إِمْتَى", "مين": "مِين",
            
            # Responses
            "ايوه": "أَيْوَة", "لا": "لَأ", "لأ": "لَأ",
            "ماشي": "مَاشِي", "طيب": "طَيِّب", "تمام": "تَمَام",
            
            # Common verbs
            "عايز": "عَايِز", "عايزه": "عَايْزَة", "عايزين": "عَايزِين",
            "بحب": "بَحِب", "بقول": "بَقُول", "بعمل": "بَعْمَل",
            
            # Time
            "دلوقتي": "دِلْوَقْتِ", "بكره": "بُكْرَة", 
            "النهارده": "النَّهَارْدَة", "امبارح": "إِمْبَارِح",
            
            # Place and geography
            "مصر": "مَصْر", "القاهرة": "القَاهِرَة",
            
            # Objects
            "الميه": "المَيَّة", "الاكل": "الأَكْل", 
            "الشغل": "الشُّغْل", "البيت": "البِيت",
            
            # Adjectives
            "جميل": "جَمِيل", "كبير": "كْبِير", "صغير": "صُغَيَّر",
            "كويس": "كْوَيِّس", "حلو": "حِلْو",
            
            # Misc
            "يا": "يَا", "شاطر": "شَاطِر", "برافو": "بْرَافُو",
            "الاخبار": "الأَخْبَار", "سكر": "سُكَّر",
            "شوفتي": "شُفْتِي", "في": "فِي",
        }

    def normalize_for_tts(self, text):
        """Normalize Arabic text with comprehensive tashkeel for Egyptian TTS."""
        if not text: 
            return ""
        
        # 1. Replace ta marbuta with ha
        text = text.replace("ة", "ه")
        
        # 2. Normalize alef variations (keep hamza for natural pronunciation)
        text = text.replace("أ", "ا").replace("إ", "ا")
        
        # 3. Apply MSA to Egyptian conversions with regex
        for pattern, replacement in self.msa_to_egy.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # 4. Apply word-level tashkeel
        words = text.split()
        final_words = []
        
        for word in words:
            # Clean the word for dictionary lookup
            clean_word = word.strip(".,،؛:!؟?")
            
            # Check if word is in diacritics dictionary
            if clean_word in self.egy_diacritics:
                # Replace the cleaned part but keep punctuation
                diacritic_word = self.egy_diacritics[clean_word]
                # Re-add any punctuation that was stripped
                for punct in ".,،؛:!؟?":
                    if word.endswith(punct):
                        diacritic_word += punct
                final_words.append(diacritic_word)
            else:
                # If not in dictionary, add basic tashkeel to common patterns
                final_words.append(self._add_basic_tashkeel(word))
        
        result = " ".join(final_words)
        
        # 5. Final cleanup - ensure proper spacing around tashkeel
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result
    
    def _add_basic_tashkeel(self, word):
        """Add basic tashkeel to words not in dictionary."""
        if not word or len(word) < 2:
            return word
        
        # Skip words that already have tashkeel
        tashkeel_chars = "َُِّْ"
        if any(char in word for char in tashkeel_chars):
            return word
        
        # Add fatha to common letter patterns
        # This is basic and can be enhanced
        result = word
        
        # Common Egyptian patterns
        if word.startswith("ال"):  # Articles
            result = "ال" + word[2:]
        
        return result


class TTSGenerator:
    """Voice class using Edge-TTS (Free Microsoft TTS) for Arabic pronunciation."""
    def __init__(self):
        try:
            import edge_tts
            self.edge_tts = edge_tts
            # Use Standard Arabic female voice for clear, professional pronunciation
            self.voice = os.getenv("EDGE_VOICE", "ar-SA-ZariyahNeural")  # Saudi Standard Arabic
            print(f"👄 Edge-TTS initialized with voice: {self.voice}")
            print("✅ TTS System Online (Edge-TTS - Free)")
        except ImportError:
            print("❌ edge-tts not installed. Run: pip install edge-tts")
            self.edge_tts = None
    
    async def speak_async(self, text):
        """Generate speech asynchronously and return base64 audio."""
        if not self.edge_tts or not text:
            return None
        try:
            print(f"\n🗣️  Speaking: {text}")
            
            # Call async function directly
            audio_bytes = await self._generate_audio(text)
            
            if audio_bytes:
                return base64.b64encode(audio_bytes).decode("utf-8")
            return None
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            return None
    
    def speak(self, text):
        """Sync wrapper - tries to use existing event loop or creates new one."""
        if not self.edge_tts or not text:
            return None
        try:
            # Check if there's a running event loop
            loop = None
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                pass
            
            if loop and loop.is_running():
                # We're in an async context - create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._generate_audio(text))
                    audio_bytes = future.result(timeout=30)
            else:
                # No running loop - safe to use asyncio.run()
                audio_bytes = asyncio.run(self._generate_audio(text))
            
            print(f"\n🗣️  Speaking: {text}")
            if audio_bytes:
                return base64.b64encode(audio_bytes).decode("utf-8")
            return None
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            return None
    
    async def _generate_audio(self, text):
        """Async helper to generate audio with edge-tts."""
        import tempfile
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Generate audio
            communicate = self.edge_tts.Communicate(text, self.voice)
            await communicate.save(tmp_path)
            
            # Read audio bytes
            with open(tmp_path, 'rb') as f:
                audio_bytes = f.read()
            
            return audio_bytes
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class ArabicTTSGenerator:
    """
    Wrapper for Arabic TTS using Edge-TTS.
    Uses Standard Arabic for clear, professional narration.
    """
    
    def __init__(self):
        # Simplified - no heavy dialect processing for clearer speech
        self.speaker = TTSGenerator()
    
    async def generate_arabic_audio_async(self, arabic_text: str, output_path: str) -> dict:
        """
        Generate Arabic audio file from text asynchronously.
        
        Args:
            arabic_text: Arabic text to convert to speech
            output_path: Where to save the MP3 file
            
        Returns:
            dict with success, audio_path, error
        """
        try:
            # Use text as-is for clear, simple Standard Arabic
            print(f"  ✨ Text: {arabic_text[:80]}...")
            
            # Get audio as base64 from voice class using async
            audio_base64 = await self.speaker.speak_async(arabic_text)
            
            if audio_base64:
                # Decode and save to file
                audio_bytes = base64.b64decode(audio_base64)
                
                # Ensure directory exists
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(audio_bytes)
                
                return {
                    "success": True,
                    "audio_path": output_path,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "audio_path": None,
                    "error": "TTS returned no audio"
                }
                
        except Exception as e:
            return {
                "success": False,
                "audio_path": None,
                "error": str(e)
            }
    
    def generate_arabic_audio(self, arabic_text: str, output_path: str) -> dict:
        """
        Generate Arabic audio file from text (sync wrapper).
        
        Args:
            arabic_text: Arabic text to convert to speech
            output_path: Where to save the MP3 file
            
        Returns:
            dict with success, audio_path, error
        """
        try:
            # Use text as-is for clear, simple Standard Arabic
            print(f"  ✨ Text: {arabic_text[:80]}...")
            
            # Get audio as base64 from voice class
            audio_base64 = self.speaker.speak(arabic_text)
            
            if audio_base64:
                # Decode and save to file
                audio_bytes = base64.b64decode(audio_base64)
                
                # Ensure directory exists
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(audio_bytes)
                
                return {
                    "success": True,
                    "audio_path": output_path,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "audio_path": None,
                    "error": "TTS returned no audio"
                }
                
        except Exception as e:
            return {
                "success": False,
                "audio_path": None,
                "error": str(e)
            }


# Singleton instance for reuse
_tts_instance = None

def get_arabic_tts() -> ArabicTTSGenerator:
    """Get or create Arabic TTS generator singleton."""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = ArabicTTSGenerator()
    return _tts_instance


async def generate_arabic_narration_async(arabic_text: str, output_path: str) -> dict:
    """
    Async function to generate Arabic audio (for use in pipelines).
    
    Args:
        arabic_text: Text in Arabic to narrate
        output_path: Path to save the MP3 file
        
    Returns:
        dict with success, audio_path, error
    """
    tts = get_arabic_tts()
    return await tts.generate_arabic_audio_async(arabic_text, output_path)


def generate_arabic_narration(arabic_text: str, output_path: str) -> dict:
    """
    Convenience function to generate Arabic audio (sync wrapper).
    
    Args:
        arabic_text: Text in Arabic to narrate
        output_path: Path to save the MP3 file
        
    Returns:
        dict with success, audio_path, error
    """
    tts = get_arabic_tts()
    return tts.generate_arabic_audio(arabic_text, output_path)


if __name__ == "__main__":
    # Test the wrapper
    test_text = "مرحبا، هذا اختبار للنظام الصوتي"
    result = generate_arabic_narration(test_text, "test_arabic.mp3")
    print(f"Result: {result}")
