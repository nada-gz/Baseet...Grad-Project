"""
Image processing utilities - Resize and prepare images for video.
"""
import os
import hashlib
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO
from serpapi import GoogleSearch

from config import VIDEO_WIDTH, VIDEO_HEIGHT, IMAGE_OUTPUT_DIR, SERPAPI_KEY


def resize_image_for_video(image_path: str, output_path: str = None, 
                           max_width: int = None, max_height: int = None) -> str:
    """
    Resize image to fit within video frame while maintaining aspect ratio.
    
    Args:
        image_path: Path to source image
        output_path: Where to save resized image (optional, modifies in place if None)
        max_width: Maximum width (default: VIDEO_WIDTH * 0.8)
        max_height: Maximum height (default: VIDEO_HEIGHT * 0.8)
        
    Returns:
        Path to resized image
    """
    max_width = max_width or int(VIDEO_WIDTH * 0.8)
    max_height = max_height or int(VIDEO_HEIGHT * 0.8)
    
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (handles PNGs with transparency)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Calculate new size maintaining aspect ratio
            width, height = img.size
            ratio = min(max_width / width, max_height / height)
            
            if ratio < 1:  # Only resize if image is larger than target
                new_size = (int(width * ratio), int(height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Save
            save_path = output_path or image_path
            img.save(save_path, 'PNG', quality=95)
            return save_path
            
    except Exception as e:
        print(f"  ⚠️ Image resize failed: {e}")
        return image_path  # Return original on failure


def search_and_download_image(concept: str, session_dir: Path = None) -> dict:
    """
    Search for educational image and download with proper sizing.
    
    Args:
        concept: Search concept
        session_dir: Session directory for output (uses global IMAGE_OUTPUT_DIR if None)
        
    Returns:
        dict with success, path, error
    """
    if not SERPAPI_KEY:
        return {"success": False, "path": None, "error": "SERPAPI_KEY not set"}
    
    output_dir = (session_dir / "images") if session_dir else IMAGE_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create cache filename from concept
    cache_name = hashlib.md5(concept.encode()).hexdigest()
    cache_path = output_dir / f"{cache_name}.png"
    
    # Check cache first
    if cache_path.exists():
        return {"success": True, "path": str(cache_path), "error": None, "cached": True}
    
    try:
        # Search with SerpAPI
        search = GoogleSearch({
            "q": f"{concept} educational diagram high quality",
            "tbm": "isch",
            "tbs": "il:cl,isz:l",  # Creative Commons + Large size
            "api_key": SERPAPI_KEY
        })
        
        images = search.get_dict().get("images_results", [])
        if not images:
            return {"success": False, "path": None, "error": "No images found"}
        
        # Try first few results
        url = None
        for img in images[:5]:
            candidate = img.get("original")
            if candidate and any(ext in candidate.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                url = candidate
                break
        
        if not url:
            url = images[0].get("original")
        
        if not url:
            return {"success": False, "path": None, "error": "No valid image URL"}
        
        # Download
        response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        
        # Load and resize
        img = Image.open(BytesIO(response.content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Resize to fit video frame
        max_width = int(VIDEO_WIDTH * 0.7)
        max_height = int(VIDEO_HEIGHT * 0.7)
        width, height = img.size
        ratio = min(max_width / width, max_height / height)
        
        if ratio < 1:
            new_size = (int(width * ratio), int(height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        img.save(cache_path, 'PNG')
        
        return {"success": True, "path": str(cache_path), "error": None, "cached": False}
        
    except Exception as e:
        return {"success": False, "path": None, "error": str(e)}


if __name__ == "__main__":
    # Test
    from config import init_output_dirs
    init_output_dirs()
    
    result = search_and_download_image("mitochondria cell diagram")
    print(f"Result: {result}")
