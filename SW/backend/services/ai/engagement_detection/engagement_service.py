from pathlib import Path
from io import BytesIO
from PIL import Image
from transformers import pipeline

MODEL_DIR = Path(__file__).resolve().parent / "model"

classifier = pipeline(
    "image-classification",
    model=str(MODEL_DIR)
)

def run_engagement_check(image_bytes: bytes) -> dict:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    results = classifier(image)
    top = results[0]
    return {
        "label": top["label"],
        "score": round(float(top["score"]), 4),
        "all_results": results
    }