import os
import sys
import subprocess
import json
import time
import re
from colorama import Fore, init
from dotenv import load_dotenv
import base64
from gradio_client import Client


# 1. تهيئة البيئة
load_dotenv()
init(autoreset=True)

# 2. إعداد المسارات
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")
SHARED_FILE = os.path.join(current_dir, "shared_data.json")
if os.path.exists(env_path): load_dotenv(dotenv_path=env_path)

class TextPostProcessor:
    def __init__(self):
        self.msa_to_egy = {
            r"\bحبيبي\b": "حَبِيبِي",       # بتشكيل يضمن الحنية
            r"\bعامل ايه\b": "عَامِل إِيه", # النطق المصري لـ "شو الأخبار"
            r"\bيا بطل\b": "يَا بَطَل",
            r"\bيا شطورة\b": "يَا شَطُّورَه",
            # --- ضبط الضمائر (أهم حاجة طلبتيها) ---
            r"\bانت\b": "إِنْتِي",        # للمؤنث بنطق صريح
            r"\bأنت\b": "إِنْتِي",
            r"\bانتَ\b": "إِنْتَا",        # للمذكر
            r"\bانتا\b": "إِنْتَا",
            r"\bانت\b": "إِنْتَا",
            r"\bأنت\b": "إِنْتِي",         # افتراضي للمؤنث بما إن الصوت بنت
            # --- 🟢 (1) تظبيط "إيه الأخبار" و "النباتات" ---
            r"\bاي الاخبار\b": "إِيه الْأَخْبَار",
            r"\bايه الاخبار\b": "إِيه الْأَخْبَار",
            r"\bما الاخبار\b": "إِيه الْأَخْبَار",
            
            # النباتات الخضراء -> خضره (بالهاء)
            r"\bالنباتات الخضراء\b": "النَّبَاتَات الْخَضْرَه",
            r"\bالنباتات الخضرا\b": "النَّبَاتَات الْخَضْرَه",
            r"\bنباتات\b": "نَبَاتَات",

            # --- 🟢 (2) الحل السحري للجيم المصرية (حرف گ) ---
            r"\bالحديقة\b": "الْگِنِينَه", 
            r"\bالجنينة\b": "الْگِنِينَه",
            r"\bجنينة\b": "گِنِينَه",
            
            r"\bجميل\b": "گَمِيل",        # جيم مصرية
            r"\bجديد\b": "گِدِيد",
            r"\bجاهز\b": "گَاهِز",

            # --- 🟢 (3) تظبيط "إزيك" بكل أشكالها ---
            r"\bكيف حالك\b": "إِزَّيَّك",   # (Iz-zay-yak)
            r"\bكيفك\b": "إِزَّيَّك",
            r"\bازيك\b": "إِزَّيَّك",       # حتى لو كتبتيها من غير همزة
            r"\bإزيك\b": "إِزَّيَّك",
            r"\bكيف\b": "إِزَّاي",
            
            # --- 🟢 (4) تحويلات اللهجة العامية ---
            r"\bجدا\b": "أَوِي",          
            r"\bجيد\b": "تَمَام",         
            r"\bمسجد\b": "الْجَامِع",     
            r"\bصديقي\b": "صَاحْبِي",
            r"\bقولي\b": "قُولِي",
            r"\bقلي\b": "قُولِي",
            
            r"\bهذا\b": "دَه", r"\bهذه\b": "دِي", 
            r"\bسوف\b": "هَـ", r"\bنحن\b": "إِحْنَا", 
            r"\bلماذا\b": "لِيه بَس", 
            r"\bالآن\b": "دِلْوَقْتِي", r"\bحسنا\b": "مَاشِي", 
            r"\bماذا\b": "إِيه",
            
            r"\bأريد\b": "عايْزَه", 
            r"\bلا\b": "لَأ", 
            r"\bنعم\b": "أَيْوَة",
            r"\bيا\b": "يَا",
            r"\bغدا\b": "بُكْرَه",

            r"\bالماء\b": "الْمَيَّه", 
            r"\bمياه\b": "مَيَّه",
            r"\bماء\b": "مَيَّه",
            r"\bشكرا\b": "شُكْراً",
        }
        
        # قاموس التشكيل عشان النطق يبقى سليم
        self.egy_diacritics = {
            "انا": "أَنَا", "هو": "هُوَ", "هي": "هِيَّ",
            "احنا": "إِحْنَا", "ده": "دَه", "دي": "دِي", "عشان": "عَشَان",
            "كده": "كِدَه", "ايه": "إِيه", "مصر": "مَصْر", 
            "يا": "يَا", "شاطر": "شَاطِر", "برافو": "بْرَافُو",
            "عايزه": "عايْزَه", "الميه": "الْمَيَّه", "الاخبار": "الْأَخْبَار"
        }

    def normalize_for_tts(self, text):
        if not text: return ""
        
        # 1. استبدال التاء المربوطة بـ هاء (القاعدة الذهبية)
        text = text.replace("ة", "ه").replace("اء ", "ه ")

        # 2. توحيد الألفات
        text = text.replace("أ", "ا").replace("إ", "ا")
        
        # 3. تطبيق القاموس
        for pattern, replacement in self.msa_to_egy.items():
            text = re.sub(pattern, replacement, text)
        
        # 4. التشكيل النهائي
        words = text.split()
        final_words = []
        for word in words:
            # لو الكلمة فيها حرف (گ) سيبها زي ما هي عشان الـ AI ينطقها G
            if "گ" in word:
                final_words.append(word)
                continue
                
            clean_word = word.replace("ا", "ا")
            if clean_word in self.egy_diacritics:
                final_words.append(self.egy_diacritics[clean_word])
            elif word in self.egy_diacritics:
                final_words.append(self.egy_diacritics[word])
            else:
                final_words.append(word)
                
        return " ".join(final_words)

class TTSGenerator:
    def __init__(self):
        print(Fore.YELLOW + "👄 Connecting to Gradio TTS API...")
        try:
            self.client = Client("niletts-tts/niletts-api")
            print(Fore.GREEN + "✅ TTS System Online (Gradio)")
        except Exception as e:
            print(Fore.RED + f"❌ Connection Error: {e}")

    def speak(self, text):
        if not text: return None
        print(Fore.MAGENTA + f"\n🗣️  Speaking: {text}")
        try:
            filepath = self.client.predict(
                text=text,
                api_name="/generate_speech",
            )
            
            with open(filepath, "rb") as f:
                audio_bytes = f.read()
            
            try:
                print(Fore.YELLOW + "🔊 Playing audio locally...")
                temp_file = os.path.join(current_dir, "temp_voice.mp3")
                with open(temp_file, "wb") as f:
                    f.write(audio_bytes)
                
                if sys.platform == "win32":
                    os.startfile(temp_file)
                elif sys.platform == "darwin":
                    subprocess.call(["open", temp_file])
                else:
                    subprocess.call(["xdg-open", temp_file])
            except: pass
            
            return base64.b64encode(audio_bytes).decode("utf-8")

        except Exception as e:
            print(Fore.RED + f"❌ TTS Error: {e}")
            return None

def create_test_file():
    # جملة الاختبار عشان تتأكدي إن كله تمام
    data = {"raw_text": "ازيك يا سكر، ايه الاخبار؟ شوفتي النباتات الخضرا في الجنينة؟", "status": "new", "timestamp": time.time() + 5}
    try:
        os.makedirs(os.path.dirname(SHARED_FILE), exist_ok=True)
        with open(SHARED_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except: pass

def main():
    print(Fore.WHITE + "="*50)
    print(Fore.WHITE + "🚀 TTS PROCESSOR (FINAL EGYPTIAN VERSION)")
    print(Fore.WHITE + "="*50)
    if not os.path.exists(SHARED_FILE): create_test_file()

    processor = TextPostProcessor()
    tts_engine = TTSGenerator()
    last_processed_time = 0
    print(Fore.CYAN + "👀 Waiting for new text...")

    while True:
        try:
            processed_something = False
            if os.path.exists(SHARED_FILE):
                try:
                    with open(SHARED_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except: time.sleep(0.5); continue
                
                if data.get("status") == "new" and data.get("timestamp", 0) > last_processed_time:
                    raw_text = data.get("raw_text", "")
                    if raw_text:
                        print(Fore.WHITE + f"\n📥 Received: {raw_text}")
                        clean_text = processor.normalize_for_tts(raw_text)
                        print(Fore.GREEN + f"✨ Processed: {clean_text}")
                        audio_base64 = tts_engine.speak(clean_text)
                        
                        if audio_base64:
                            data["status"] = "processed"
                            data["audio_base64"] = audio_base64
                            with open(SHARED_FILE, 'w', encoding='utf-8') as f:
                                json.dump(data, f, ensure_ascii=False, indent=4)
                            print(Fore.CYAN + "✅ Success!")
                        else:
                            data["status"] = "error"
                            with open(SHARED_FILE, 'w', encoding='utf-8') as f:
                                json.dump(data, f, ensure_ascii=False, indent=4)
                        last_processed_time = data.get("timestamp", 0)
                        processed_something = True
            if not processed_something: time.sleep(1)
        except KeyboardInterrupt: break
        except Exception: time.sleep(1)

if __name__ == "__main__":
    main()