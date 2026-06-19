from transformers import pipeline
from pathlib import Path

MODEL_ID = "gowdaman/gowdaman-emotion-detection"
LOCAL_DIR = Path(__file__).resolve().parent / "model"

def main():
    print("Downloading model...")
    clf = pipeline("image-classification", model=MODEL_ID)
    clf.save_pretrained(str(LOCAL_DIR))
    print(f"Model saved to: {LOCAL_DIR}")

if __name__ == "__main__":
    main()