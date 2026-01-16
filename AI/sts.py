import os
import time
import re
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import torch
import librosa
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from colorama import Fore, Style, init

# Initialize colorama for colored logs
init(autoreset=True)

# =======================================================
# ⚙️ SYSTEM CONFIGURATION (CONTROL PANEL)
# =======================================================

# 1. API KEYS & MODELS
# ⚠️ REPLACE WITH YOUR NEW KEY
ELEVENLABS_API_KEY = "sk_88a420f07fa5bfec9214a5f5cc55945edfb2a5b6097fe4d4"
VOICE_ID = "BZgkqPqms7Kj9ulSkVzn"  # Salma's Voice
STT_MODEL_ID = "IbrahimAmin/egyptian-arabic-wav2vec2-xlsr-53"

# 2. OPERATION MODE (THE SWITCH) 🎚️
# Set to False to test the pipeline immediately (Mock Mode).
# Set to True when you want to connect your actual RAG Model.
USE_REAL_RAG = False 

# =======================================================
# 🛠️ CLASS 1: ADVANCED PRE-PROCESSOR (The Filter)
# =======================================================
class TextPostProcessor:
    """
    Handles Text Normalization, Dialect Adaptation, and Diacritics Injection.
    Ensures the output text is optimized for Egyptian TTS pronunciation.
    """
    def __init__(self):
        # A. MSA to Egyptian Regex Map
        self.msa_to_egy = {
            r"\bهذا\b": "دَه",           # This (M) -> Da
            r"\bهذه\b": "دِي",           # This (F) -> De
            r"\bسوف\b": "هَـ",           # Will -> Ha
            r"\bنحن\b": "إِحْنَا",       # We -> Ehna
            r"\bلماذا\b": "لِيه",        # Why -> Leh
            r"\bكيف\b": "إِزَّاي",       # How -> Ezzay
            r"\bالآن\b": "دِلْوَقْتِي",  # Now -> Delwa'ty
            r"\bحسنا\b": "طَيِّب",       # Okay -> Tayeb
            r"\bجدا\b": "أَوِي",         # Very -> Awi
            r"\bأيضا\b": "كَمَان",       # Also -> Kaman
            r"\bولكن\b": "بَس",          # But -> Bas
            r"\bماذا\b": "إِيه"          # What -> Eh
        }

        # B. Egyptian Diacritics Dictionary (Forcing Correct Pronunciation)
        self.egy_diacritics = {
            "انا": "أَنَا", "انت": "أَنْتَ", "انتي": "أَنْتِي",
            "هو": "هُوَ", "هي": "هِيَّ", "احنا": "إِحْنَا",
            "ده": "دَه", "دي": "دِي", "عشان": "عَشَان",
            "كده": "كِدَه", "ايه": "إِيه", "لا": "لَأ",
            "نعم": "أَيْوَة", "شكرا": "شُكْراً", "خلاص": "خَلَاص",
            "يا": "يَااا", "مصر": "مَصْر", "القلب": "الْقَلْب",
            "الجسم": "الْجِسْم", "الدم": "الدَّم", "صحيح": "صَحِيح",
            "غلط": "غَلَط", "بسرعة": "بِسُرْعَة", "شاطر": "شَاطِر"
        }

    def normalize_for_tts(self, text):
        if not text: return ""
        
        # 1. Basic Cleaning
        text = text.replace("*", "").replace("#", "").replace("- ", "")
        text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه")
        
        # 2. Apply Dialect Conversion
        for pattern, replacement in self.msa_to_egy.items():
            text = re.sub(pattern, replacement, text)

        # 3. Inject Diacritics
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

# =======================================================
# 🧠 CLASS 2: THE BRAINS (Option 1 & Option 2)
# =======================================================

# --- OPTION 1: MOCK BRAIN (FOR TESTING) ---
class MockBrain:
    """
    Used when USE_REAL_RAG = False.
    Returns hardcoded responses to test the pipeline connectivity.
    """
    def generate_answer(self, user_query):
        print(Fore.BLUE + f"🔍 [MOCK MODE] Simulating RAG response for: {user_query}")
        
        if "قلب" in user_query:
            return "القلب هو عضو عضلي، وسوف يضخ الدم في الجسم كله."
        elif "ازيك" in user_query or "عامل" in user_query:
            return "انا بخير جدا، انت عامل ايه يا بطل؟"
        elif "اسمك" in user_query:
            return "انا سلمى، الروبوت الذكي."
        else:
            return f"انا سمعتك بتقول {user_query}، بس لسه بذاكر المنهج."

# --- OPTION 2: REAL RAG BRAIN (FOR FINAL DEPLOYMENT) ---
class RealRAGBrain:
    """
    Used when USE_REAL_RAG = True.
    Connects to your actual Content Generator / RAG Model.
    """
    def __init__(self):
        print(Fore.BLUE + "🧠 Initializing Real RAG Model...")
        # -----------------------------------------------------
        # TODO: Initialize your model here
        # Example: self.qa_chain = load_qa_chain(...)
        # -----------------------------------------------------
        pass

    def generate_answer(self, user_query):
        print(Fore.BLUE + f"🔍 [REAL RAG MODE] Generating content for: {user_query}...")
        
        # -----------------------------------------------------
        # TODO: PASTE YOUR RAG INFERENCE CODE HERE
        # Example: response = self.qa_chain.run(user_query)
        # return response
        # -----------------------------------------------------
        
        # Temporary placeholder until you paste your code:
        return "Please paste your RAG code inside the RealRAGBrain class."

# =======================================================
# 👂 CLASS 3: HEARING UNIT (STT)
# =======================================================
class EgyptianEar:
    def __init__(self):
        print(Fore.YELLOW + "👂 Loading Wav2Vec2 Model (IbrahimAmin)...")
        try:
            self.processor = Wav2Vec2Processor.from_pretrained(STT_MODEL_ID)
            self.model = Wav2Vec2ForCTC.from_pretrained(STT_MODEL_ID)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            print(Fore.GREEN + f"✅ STT Ready on: {self.device}")
        except Exception as e:
            print(Fore.RED + f"❌ Error loading STT: {e}")

    def listen(self, filename="temp_in.wav"):
        print(Fore.CYAN + "\n🎤 Press [Enter] to start recording...")
        input()
        print(Fore.RED + "🔴 Listening... (Press [Enter] to stop)")
        
        recording = []
        def callback(indata, frames, time, status):
            recording.append(indata.copy())
            
        with sd.InputStream(samplerate=16000, channels=1, callback=callback):
            input() 
            
        if not recording: return ""
        
        full_rec = np.concatenate(recording, axis=0)
        write(filename, 16000, full_rec)
        
        try:
            speech, _ = librosa.load(filename, sr=16000)
            inputs = self.processor(speech, sampling_rate=16000, return_tensors="pt", padding=True)
            with torch.no_grad():
                logits = self.model(inputs.input_values.to(self.device)).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = self.processor.batch_decode(predicted_ids)[0]
            return transcription
        except:
            return ""

# =======================================================
# 👅 CLASS 4: SPEAKING UNIT (TTS)
# =======================================================
class SalmaTongue:
    def __init__(self):
        print(Fore.YELLOW + "👄 Connecting to ElevenLabs...")
        try:
            self.client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
            self.voice_id = VOICE_ID
            print(Fore.GREEN + "✅ TTS System Online")
        except:
            print(Fore.RED + "❌ Check API Key")

    def speak(self, text):
        if not text: return
        print(Fore.MAGENTA + f"🗣️  Salma (Final Output): {text}")
        try:
            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id="eleven_multilingual_v2" 
            )
            save(audio, "output.mp3")
            if os.name == 'nt': os.startfile("output.mp3")
            else: os.system("open output.mp3")
            time.sleep(3) 
        except Exception as e:
            print(Fore.RED + f"❌ TTS Error: {e}")

# =======================================================
# 🚀 MAIN PIPELINE EXECUTION
# =======================================================
def main():
    print(Fore.WHITE + "="*60)
    print(Fore.WHITE + "🚀 SALMA V5.0: INTEGRATED STS SYSTEM")
    print(Fore.WHITE + "="*60)

    # 1. Initialize Hardware Modules
    ear = EgyptianEar()
    tongue = SalmaTongue()
    post_processor = TextPostProcessor()
    
    # 2. Select Brain based on Configuration
    if USE_REAL_RAG:
        print(Fore.CYAN + "⚙️  Mode Selected: REAL RAG INTELLIGENCE")
        brain = RealRAGBrain()
    else:
        print(Fore.CYAN + "⚙️  Mode Selected: MOCK TESTING (Offline Logic)")
        brain = MockBrain()

    # Welcome
    tongue.speak("أهلاً يا بطل، أنا جاهزة.")

    while True:
        try:
            # --- STEP 1: HEARING ---
            user_query = ear.listen()
            print(Fore.WHITE + f"📝 Input: {user_query}")
            
            if not user_query.strip(): continue

            if "باي" in user_query or "سلام" in user_query:
                tongue.speak("مع السلامة.")
                break

            # --- STEP 2: GENERATION (Mock or Real) ---
            raw_answer = brain.generate_answer(user_query)
            print(Fore.CYAN + f"⚙️  Raw Output: {raw_answer}")

            # --- STEP 3: PRE-PROCESSING (The Secret Sauce) ---
            clean_answer = post_processor.normalize_for_tts(raw_answer)
            print(Fore.GREEN + f"✨ Optimized Text: {clean_answer}")

            # --- STEP 4: SPEAKING ---
            tongue.speak(clean_answer)

        except KeyboardInterrupt:
            print("\n👋 Shutting down.")
            break

if __name__ == "__main__":
    main()