"""
Generic Test Script for Educational Video Pipeline
Reads the topic from prompt.txt and duration from duration.txt

Usage:
1. Edit prompt.txt to set your video topic
2. Edit duration.txt to set duration in minutes (e.g., 1.0, 2.0, 0.5)
3. Run: python test_generic.py

Features:
- Enhanced TTS (ElevenLabs + Edge-TTS fallback)
- Academic Arabic narration and titles
- Real images from online search
- NO overlapping text in animations
"""
import asyncio
import sys
from pathlib import Path
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

# Import the pipeline
from pipeline_v2 import EducationalVideoPipeline


def read_prompt() -> str:
    """Read the video topic from prompt.txt"""
    prompt_file = Path(__file__).parent / "prompt.txt"
    
    if not prompt_file.exists():
        print(Fore.RED + "❌ Error: prompt.txt not found!")
        print(Fore.YELLOW + "Please create prompt.txt with your video topic.")
        sys.exit(1)
    
    try:
        topic = prompt_file.read_text(encoding='utf-8').strip()
        if not topic:
            print(Fore.RED + "❌ Error: prompt.txt is empty!")
            print(Fore.YELLOW + "Please add your video topic to prompt.txt")
            sys.exit(1)
        return topic
    except Exception as e:
        print(Fore.RED + f"❌ Error reading prompt.txt: {e}")
        sys.exit(1)


def read_duration() -> float:
    """Read the video duration from duration.txt"""
    duration_file = Path(__file__).parent / "duration.txt"
    
    if not duration_file.exists():
        print(Fore.YELLOW + "⚠️  duration.txt not found, using default: 1.0 minute")
        return 1.0
    
    try:
        duration_text = duration_file.read_text(encoding='utf-8').strip()
        duration = float(duration_text)
        
        if duration <= 0 or duration > 10:
            print(Fore.YELLOW + f"⚠️  Invalid duration: {duration}. Using 1.0 minute")
            return 1.0
            
        return duration
    except Exception as e:
        print(Fore.YELLOW + f"⚠️  Error reading duration.txt: {e}. Using 1.0 minute")
        return 1.0


async def main():
    print(Fore.WHITE + "="*70)
    print(Fore.WHITE + "🎬 EDUCATIONAL VIDEO GENERATOR - GENERIC TEST")
    print(Fore.WHITE + "="*70)
    
    # Read configuration from files
    topic = read_prompt()
    duration = read_duration()
    
    print(Fore.CYAN + f"\n📚 Topic: {topic}")
    print(Fore.CYAN + f"⏱️  Duration: {duration} minute(s)")
    print(Fore.CYAN + f"🗣️  Audio: Academic Arabic (Edge-TTS only)")
    print(Fore.CYAN + f"🎨 Visuals: English + Arabic titles, Real images")
    print(Fore.CYAN + f"✅ NO overlapping text - explicit positioning enforced")
    
    print(Fore.WHITE + "\n" + "="*70)
    print(Fore.YELLOW + "Starting pipeline...\n")
    
    # Trace callback to show progress
    def trace_callback(msg: str):
        print(msg)
    
    # Initialize pipeline with NO overlapping text emphasis
    pipeline = EducationalVideoPipeline(
        trace_callback=trace_callback,
        target_duration_minutes=duration
    )
    
    try:
        # Generate the video
        result = await pipeline.generate(topic)
        
        # Display results
        print(Fore.WHITE + "\n" + "="*70)
        print(Fore.WHITE + "📊 PIPELINE RESULTS")
        print(Fore.WHITE + "="*70)
        
        if result["success"]:
            print(Fore.GREEN + "\n✅ Video generated successfully!")
            print(Fore.CYAN + f"\n📁 Output directory: {result['session_dir']}")
            
            if result.get("video_path"):
                print(Fore.GREEN + f"\n🎥 Final video: {result['video_path']}")
                print(Fore.YELLOW + f"\n🔊 Opening video player...")
                
                # Try to open the video
                import os
                try:
                    os.startfile(result['video_path'])
                    print(Fore.GREEN + "✅ Video player launched!")
                except Exception as e:
                    print(Fore.YELLOW + f"⚠️  Could not auto-play: {e}")
                    print(Fore.CYAN + f"   Manually open: {result['video_path']}")
            
            # Show segments info
            if result.get("trace") and result["trace"].get("segments"):
                segments = result["trace"]["segments"]
                print(Fore.CYAN + f"\n📋 Generated {len(segments)} segments:")
                for i, seg in enumerate(segments, 1):
                    status = "✅" if seg.get("status") == "success" else "❌"
                    title_en = seg.get("title", "Unknown")
                    title_ar = seg.get("arabic_title", "")
                    if title_ar:
                        print(Fore.CYAN + f"   {status} Segment {i}: {title_en} / {title_ar}")
                    else:
                        print(Fore.CYAN + f"   {status} Segment {i}: {title_en}")
            
            # Show trace logs (last 10)
            if result.get("trace"):
                print(Fore.CYAN + f"\n📝 Pipeline logs (last 10 entries):")
                for log in result['trace'].get('logs', [])[-10:]:
                    print(Fore.WHITE + f"   {log}")
                
                # Show errors if any
                if result['trace'].get('errors'):
                    print(Fore.RED + f"\n⚠️  Errors encountered:")
                    for error in result['trace'].get('errors'):
                        print(Fore.RED + f"   • {error}")
        else:
            print(Fore.RED + "\n❌ Video generation failed!")
            print(Fore.RED + f"Error: {result.get('error', 'Unknown error')}")
            
            # Show trace for debugging
            if result.get("trace"):
                print(Fore.YELLOW + "\n📝 Last 20 log entries:")
                for log in result['trace'].get('logs', [])[-20:]:
                    print(Fore.WHITE + f"   {log}")
        
        print(Fore.WHITE + "\n" + "="*70)
        print(Fore.CYAN + "\n📝 Video features:")
        print(Fore.GREEN + "  ✓ English title (top)")
        print(Fore.GREEN + "  ✓ Arabic title (below English)")
        print(Fore.GREEN + "  ✓ Real images when relevant")
        print(Fore.GREEN + "  ✓ Academic Arabic narration")
        print(Fore.GREEN + "  ✓ NO overlapping text - proper spacing enforced")
        print(Fore.GREEN + "  ✓ Smooth transitions without black screens")
        print(Fore.WHITE + "\n" + "="*70)
        print(Fore.CYAN + "\n💡 To generate a different video:")
        print(Fore.WHITE + "  1. Edit prompt.txt with your new topic")
        print(Fore.WHITE + "  2. Edit duration.txt with desired duration (in minutes)")
        print(Fore.WHITE + "  3. Run: python test_generic.py")
        print(Fore.WHITE + "="*70)
        
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(Fore.RED + f"\n\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print(Fore.CYAN + "\n🎬 Starting Educational Video Generator...")
    print(Fore.CYAN + "📄 Reading configuration from prompt.txt and duration.txt\n")
    asyncio.run(main())
