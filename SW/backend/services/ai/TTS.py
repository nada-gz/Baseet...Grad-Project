import os
import json
import time
import re
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from colorama import Fore, init
from dotenv import load_dotenv

# 1. Initialize environment and colors
load_dotenv()
init(autoreset=True)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")
# SHARED_FILE = r"Z:\content_grad\Grad-Project\SW\backend\services\ai\shared_data.json"

class TextPostProcessor:
    """
    Handles Text Normalization and Dialect Adaptation.
    """
    def __init__(self):
        self.msa_to_egy = {
            r"\bهذا\b": "دَه", r"\bهذه\b": "دِي", r"\bسوف\b": "هَـ",
            r"\bنحن\b": "إِحْنَا", r"\bلماذا\b": "لِيه", r"\bكيف\b": "إِزَّاي",
            r"\bالآن\b": "دِلْوَقْتِي", r"\bحسنا\b": "طَيِّب", r"\bجدا\b": "أَوِي",
            r"\bماذا\b": "إِيه"
        }
        self.egy_diacritics = {
            "انا": "أَنَا", "انت": "أَنْتَ", "هو": "هُوَ", "هي": "هِيَّ",
            "احنا": "إِحْنَا", "ده": "دَه", "دي": "دِي", "عشان": "عَشَان",
            "كده": "كِدَه", "ايه": "إِيه", "لا": "لَأ", "نعم": "أَيْوَة",
            "شكرا": "شُكْراً", "يا": "يَااا", "مصر": "مَصْر"
        }

    def normalize_for_tts(self, text):
        if not text: return ""
        text = text.replace("أ", "ا").replace("إ", "ا").replace("ة", "ه")
        for pattern, replacement in self.msa_to_egy.items():
            text = re.sub(pattern, replacement, text)
        
        words = text.split()
        final_words = []
        for word in words:
            clean_word = word.replace("ا", "ا")
            if clean_word in self.egy_diacritics:
                final_words.append(self.egy_diacritics[clean_word])
            elif word in self.egy_diacritics:
                final_words.append(self.egy_diacritics[word])
            else:
                final_words.append(word)
        return " ".join(final_words)

class voice:
    """
    Reads processed text and converts it to speech using ElevenLabs.
    """
    def __init__(self):
        print(Fore.YELLOW + "👄 Connecting to ElevenLabs...")
        try:
            self.client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
            self.voice_id = VOICE_ID
            print(Fore.GREEN + "✅ TTS System Online")
        except:
            print(Fore.RED + "❌ Check API Key")

    def speak(self, text):
        if not text: return None
        print(Fore.MAGENTA + f"\n🗣️  Speaking: {text}")
        try:
            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id="eleven_multilingual_v2"
            )
            # Return audio data as base64 for frontend
            import base64
            # ElevenLabs convert returns a generator of bytes
            audio_bytes = b"".join(audio)
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            
            # Optional: keep saving locally for debug if needed
            # save(audio_bytes, "output.mp3")
            
            return audio_base64
        except Exception as e:
            print(Fore.RED + f"❌ TTS Error: {e}")
            return None

def create_test_file():
    """Creates a dummy JSON file if one doesn't exist so the script runs immediately."""
    print(Fore.YELLOW + "⚠️  No JSON file found. Creating a test file...")
    data = {
        "raw_text": "مرحبا، النظام يعمل بنجاح",
        "status": "new",
        "timestamp": time.time() + 10 # Future timestamp to ensure it triggers
    }
    with open(SHARED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(Fore.GREEN + "✅ Test file created.")

def main():
    print(Fore.WHITE + "="*50)
    print(Fore.WHITE + "🚀 MODULE 2: JSON READER & TTS PROCESSOR")
    print(Fore.WHITE + "="*50)

    # Check if file exists, if not, create it so code doesn't wait forever
    if not os.path.exists(SHARED_FILE):
        create_test_file()

    processor = TextPostProcessor()
    tongue = voice()
    
    last_processed_time = 0

    print(Fore.CYAN + "👀 Watching 'shared_data.json' for new text...")

    while True:
        try:
            processed_something = False

            # Check if file exists
            if os.path.exists(SHARED_FILE):
                with open(SHARED_FILE, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {} 
                
                # Check timestamp and status
                file_timestamp = data.get("timestamp", 0)
                
                if data.get("status") == "new" and file_timestamp > last_processed_time:
                    
                    raw_text = data["raw_text"]
                    print(Fore.WHITE + f"\n📥 Received from JSON: {raw_text}")
                    
                    # 1. Pre-process
                    clean_text = processor.normalize_for_tts(raw_text)
                    print(Fore.GREEN + f"✨ Processed: {clean_text}")
                    
                    # 2. Speak
                    tongue.speak(clean_text)
                    
                    # 3. Update Status
                    last_processed_time = file_timestamp
                    data["status"] = "processed"
                    
                    # Write back to file to mark as done
                    with open(SHARED_FILE, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                        
                    print(Fore.CYAN + "✅ Marked as processed. Waiting for next...")
                    processed_something = True
            
            # Print dots so you know it's not frozen
            if not processed_something:
                print(".", end="", flush=True)

            time.sleep(1)

        except KeyboardInterrupt:
            print("\n👋 Exiting Processor.")
            break
        except Exception as e:
            print(Fore.RED + f"\n⚠️ Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()