from elevenlabs.client import ElevenLabs
from elevenlabs import save
import os  # مكتبة للتعامل مع الويندوز

# ==========================================
# 1️⃣ مفاتيحك
# ==========================================
MY_API_KEY = "sk_a32c7e1523205ddb3c3f81cb0a872179346a78230f29278d" # ضع هنا مفتاح API الخاص بك من ElevenLabs
MY_VOICE_ID = "BZgkqPqms7Kj9ulSkVzn"

# ==========================================
# 2️⃣ كلاس سلمى
# ==========================================
class SalmaTTS:
    def __init__(self):
        print("🔌 Connecting to ElevenLabs...")
        try:
            self.client = ElevenLabs(api_key=MY_API_KEY)
            self.voice_id = MY_VOICE_ID
            print("✅ Connected Successfully!")
        except Exception as e:
            print(f"❌ Connection Error: {e}")

    def speak(self, text):
        print(f"🗣️ Salma is speaking: {text}")
        try:
            # توليد الصوت (Generator)
            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id="eleven_multilingual_v2"
            )
            
            # ✅ الحل الجذري: الحفظ ثم التشغيل
            output_filename = "salma_voice.mp3"
            
            # 1. حفظ الملف
            save(audio, output_filename)
            print(f"💾 Audio saved to {output_filename}")
            
            # 2. تشغيله بمشغل الويندوز الافتراضي
            os.startfile(output_filename) 
            
        except Exception as e:
            print(f"❌ Error while speaking: {e}")

# ==========================================
# 3️⃣ التشغيل
# ==========================================
if __name__ == "__main__":
    print("🤖 Starting Salma Project...")
    salma = SalmaTTS()
    
    # الجملة
    salma.speak("   hi إزَيَّك يا بَطَل عامل إيه؟ أنا مبسوطة أوي إني بتكلم معاك النهاردة!  ")
    print("👋 Done.")