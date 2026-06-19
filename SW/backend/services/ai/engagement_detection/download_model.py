from transformers import BeitForImageClassification, AutoImageProcessor
from pathlib import Path

MODEL_ID = "nihar245/Expression-Detection-BEIT-Large"
LOCAL_DIR = Path(__file__).resolve().parent / "model"

def main():
    print("Downloading model...")
    model = BeitForImageClassification.from_pretrained(MODEL_ID)
    processor = AutoImageProcessor.from_pretrained(MODEL_ID)
    model.save_pretrained(str(LOCAL_DIR))
    processor.save_pretrained(str(LOCAL_DIR))
    print(f"Model saved to: {LOCAL_DIR}")

if __name__ == "__main__":
    main()