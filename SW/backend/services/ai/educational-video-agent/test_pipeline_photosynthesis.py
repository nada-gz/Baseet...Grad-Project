"""
Test script to generate a 60-second educational video about photosynthesis.
Uses the full pipeline with Edge-TTS for Arabic narration.
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
    print(Fore.WHITE + "🎬 EDUCATIONAL VIDEO PIPELINE TEST")
    print(Fore.WHITE + "="*70)
    
    # Configuration
    topic = "Photosynthesis process for elementary school kids"
    duration = 1.0  # 1 minute = 60 seconds
    
    print(Fore.CYAN + f"\n📚 Topic: {topic}")
    print(Fore.CYAN + f"⏱️  Duration: {duration} minute(s)")
    print(Fore.CYAN + f"🗣️  Audio: Egyptian Arabic (Edge-TTS)")
    print(Fore.CYAN + f"🎨 Visuals: English (Manim animations)")
    
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
            
            if result.get("final_video"):
                print(Fore.GREEN + f"\n🎥 Final video: {result['final_video']}")
                print(Fore.YELLOW + f"\n🔊 Opening video player...")
                
                # Try to open the video
                import os
                try:
                    os.startfile(result['final_video'])
                    print(Fore.GREEN + "✅ Video player launched!")
                except Exception as e:
                    print(Fore.YELLOW + f"⚠️  Could not auto-play: {e}")
                    print(Fore.CYAN + f"   Manually open: {result['final_video']}")
            
            # Show segments info
            if result.get("segments"):
                print(Fore.CYAN + f"\n📋 Generated {len(result['segments'])} segments:")
                for i, seg in enumerate(result['segments'], 1):
                    status = "✅" if seg.get("status") == "success" else "❌"
                    print(Fore.CYAN + f"   {status} Segment {i}: {seg.get('title', 'Unknown')}")
            
            # Show trace logs
            if result.get("trace"):
                print(Fore.CYAN + f"\n📝 Pipeline logs ({len(result['trace'].get('logs', []))} entries):")
                for log in result['trace'].get('logs', [])[-10:]:  # Show last 10
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
        
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(Fore.RED + f"\n\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print(Fore.CYAN + "\n🚀 Starting photosynthesis video generation...")
    asyncio.run(main())
