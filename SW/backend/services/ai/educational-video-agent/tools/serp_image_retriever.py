"""Image retrieval using SerpAPI for educational content."""
import os
import hashlib
import requests
from pathlib import Path
from serpapi import GoogleSearch


def search_image(concept: str, api_key: str) -> str | None:
    """Search for educational image, return URL or None."""
    print(f"🔍 {concept}")
    
    try:
        search = GoogleSearch({
            "q": f"{concept} educational diagram high quality",
            "tbm": "isch",
            "tbs": "il:cl,isz:l",  # Creative Commons + Large size
            "api_key": api_key
        })
        
        images = search.get_dict().get("images_results", [])
        if not images:
            return None
            
        # Try to get highest resolution available
        for img in images[:3]:  # Check first 3 results
            url = img.get("original")
            if url and any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png']):
                print(f"  ✓ Found: {img.get('original_width', '?')}x{img.get('original_height', '?')}")
                return url
        
        return images[0].get("original") if images else None
        
    except Exception as e:
        print(f"  ✗ {str(e)[:60]}")
        return None


def download_image(url: str, concept: str) -> str | None:
    """Download and cache image, return local path or None."""
    cache_dir = Path("assets/image_cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    cache_path = cache_dir / f"{hashlib.md5(concept.encode()).hexdigest()}.png"
    
    if cache_path.exists():
        print(f"  ✓ Cached")
        return str(cache_path)
    
    try:
        print(f"  📥 Downloading...")
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        cache_path.write_bytes(r.content)
        print(f"  ✓ Saved")
        return str(cache_path)
    except Exception as e:
        print(f"  ✗ {str(e)[:60]}")
        return None


def get_image(concept: str, api_key: str) -> dict:
    """Get educational image for concept."""
    url = search_image(concept, api_key)
    if not url:
        return {"success": False, "path": None, "error": "Not found"}
    
    path = download_image(url, concept)
    if not path:
        return {"success": False, "path": None, "error": "Download failed"}
    
    return {"success": True, "path": path, "error": None}



if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print("❌ SERPAPI_KEY not set")
        exit(1)
    
    print("Testing Image Retrieval")
    print("=" * 50)
    
    result = get_image("mitochondria structure", api_key)
    
    print("=" * 50)
    print(f"Success: {result['success']}")
    print(f"Path: {result['path']}")
    print(f"Error: {result['error']}")
    
    exit(0 if result['success'] else 1)
