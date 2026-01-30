"""
Test script to generate a 60-second educational video about the Solar System and Planets.
Uses the full pipeline with:
- Enhanced TTS (ElevenLabs + Edge-TTS fallback)
- Academic Arabic narration and titles
- Real planet images from online search
- Simple, clear Manim animations
"""
import asyncio
import sys
from pathlib import Path
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

# Import the pipeline
from pipeline_v2 import EducationalVideoPipeline

async def main():
    print(Fore.WHITE + "="*70)
    print(Fore.WHITE + "🌌 EDUCATIONAL VIDEO PIPELINE - SOLAR SYSTEM & PLANETS")
    print(Fore.WHITE + "="*70)
    
    # Configuration
    topic = "The Solar System and Planets for elementary school students"
    duration = 1.0  # 1 minute = 60 seconds
    
    print(Fore.CYAN + f"\n📚 Topic: {topic}")
    print(Fore.CYAN + f"⏱️  Duration: {duration} minute(s)")
    print(Fore.CYAN + f"🗣️  Audio: Academic Arabic (ElevenLabs + Edge-TTS fallback)")
    print(Fore.CYAN + f"🎨 Visuals: English + Arabic titles, Real planet images")
    print(Fore.CYAN + f"📝 Text: NO overlapping text - explicit positioning enforced")
    
    print(Fore.WHITE + "\n" + "="*70)
    print(Fore.YELLOW + "Starting pipeline...\n")
    
    # Trace callback to show progress
    def trace_callback(msg: str):
        print(msg)
    
    # Initialize pipeline
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
        print(Fore.CYAN + "\n🌟 Expected content:")
        print(Fore.WHITE + "  - Introduction to the Solar System")
        print(Fore.WHITE + "  - The Sun and its importance")
        print(Fore.WHITE + "  - Inner planets (Mercury, Venus, Earth, Mars)")
        print(Fore.WHITE + "  - Outer planets (Jupiter, Saturn, Uranus, Neptune)")
        print(Fore.WHITE + "\n  Each segment with:")
        print(Fore.GREEN + "    ✓ English title (top)")
        print(Fore.GREEN + "    ✓ Arabic title (below English)")
        print(Fore.GREEN + "    ✓ Real planet images")
        print(Fore.GREEN + "    ✓ Academic Arabic narration")
        print(Fore.GREEN + "    ✓ NO overlapping text")
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
    print(Fore.CYAN + "\n🪐 Starting Solar System video generation...")
    print(Fore.CYAN + "This will create a 1-minute educational video about planets.\n")
    asyncio.run(main())
