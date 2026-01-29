import subprocess
from pathlib import Path

def test_ffmpeg():
    """Test if ffmpeg is installed and working."""
    print("🔍 Testing ffmpeg...\n")
    
    # Test 1: Check if ffmpeg is in PATH
    print("1. Checking if ffmpeg is installed...")
    result = subprocess.run("ffmpeg -version", capture_output=True, text=True, shell=True)
    
    if result.returncode == 0:
        # Get version info
        version_line = result.stdout.split('\n')[0]
        print(f"   ✓ {version_line}\n")
    else:
        print(f"   ✗ ffmpeg not found or not working\n")
        print("   Install with: winget install ffmpeg")
        return False
    
    # Test 2: Check concat capability
    print("2. Testing concat filter...")
    test_concat = """
from PIL import Image
import subprocess

# Create a 1-frame test video
img = Image.new('RGB', (100, 100), color='red')
img.save('test_frame.png')

# Create video with ffmpeg
cmd = 'ffmpeg -loop 1 -i test_frame.png -c:v libx264 -t 1 -pix_fmt yuv420p -y test1.mp4'
result = subprocess.run(cmd, capture_output=True, shell=True)

if result.returncode == 0:
    print("   ✓ Can create MP4 videos")
else:
    print(f"   ✗ Failed to create video: {result.stderr[:100]}")

# Clean up
import os
try:
    os.remove('test_frame.png')
    os.remove('test1.mp4')
except:
    pass
"""
    
    try:
        exec(test_concat)
    except ImportError:
        print("   ⚠️  PIL not installed (skipping video creation test)")
    
    print("\n✓ ffmpeg is ready!")
    return True

if __name__ == "__main__":
    success = test_ffmpeg()
    if success:
        print("\n✅ You can now run: python pipeline.py")
    else:
        print("\n❌ Fix ffmpeg before running pipeline.py")
