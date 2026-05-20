"""
Video merger - Properly combines video segments with audio.

Approach:
1. Each segment: video + audio → merged segment (with audio baked in)
2. All merged segments → scaled to same resolution with audio
3. Concatenate using filter_complex for proper audio handling
"""
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Optional

from config import TEMP_DIR, OUTPUT_DIR


def check_ffmpeg() -> bool:
    """Check if ffmpeg is available."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            capture_output=True, 
            text=True
        )
        return result.returncode == 0
    except:
        return False


def get_media_duration(file_path: str) -> float:
    """Get duration of media file in seconds."""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
    except:
        return 0.0


def has_audio_track(file_path: str) -> bool:
    """Check if a video file has an audio track."""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "a",
            "-show_entries", "stream=codec_type", "-of", "csv=p=0", file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return "audio" in result.stdout
    except:
        return False


def create_segment_with_audio(video_path: str, audio_path: str, output_path: str,
                               trace_callback=None) -> bool:
    """
    Create a single segment with video and audio properly merged.
    Audio determines the final duration.
    """
    def log(msg):
        if trace_callback:
            trace_callback(msg)
        print(msg)
    
    if not Path(video_path).exists():
        log(f"    ❌ Video not found: {video_path}")
        return False
    
    if not Path(audio_path).exists():
        log(f"    ❌ Audio not found: {audio_path}")
        return False
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    video_dur = get_media_duration(video_path)
    audio_dur = get_media_duration(audio_path)
    log(f"    📊 Video: {video_dur:.1f}s, Audio: {audio_dur:.1f}s")
    
    # Merge video with audio - scale to standard size and encode both streams
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-filter_complex", 
        "[0:v]scale=854:480:force_original_aspect_ratio=decrease,pad=854:480:(ow-iw)/2:(oh-ih)/2,setsar=1[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-ac", "2",
        "-t", str(audio_dur),
        "-loglevel", "warning",
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and Path(output_path).exists():
        out_dur = get_media_duration(output_path)
        has_audio = has_audio_track(output_path)
        log(f"    ✅ Merged: {out_dur:.1f}s, has_audio={has_audio}")
        return True
    else:
        log(f"    ❌ Merge failed: {result.stderr[:200]}")
        return False


def create_silent_video(video_path: str, output_path: str, trace_callback=None) -> bool:
    """
    Create a video with silent audio track (for intro/segments without narration).
    """
    def log(msg):
        if trace_callback:
            trace_callback(msg)
        print(msg)
    
    if not Path(video_path).exists():
        log(f"    ❌ Video not found: {video_path}")
        return False
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    video_dur = get_media_duration(video_path)
    log(f"    📊 Video: {video_dur:.1f}s (adding silent audio)")
    
    # Scale video and add silent audio
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-filter_complex",
        "[0:v]scale=854:480:force_original_aspect_ratio=decrease,pad=854:480:(ow-iw)/2:(oh-ih)/2,setsar=1[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-ac", "2",
        "-t", str(video_dur),
        "-loglevel", "warning",
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and Path(output_path).exists():
        out_dur = get_media_duration(output_path)
        has_audio = has_audio_track(output_path)
        log(f"    ✅ Silent video: {out_dur:.1f}s, has_audio={has_audio}")
        return True
    else:
        log(f"    ❌ Silent video failed: {result.stderr[:200]}")
        return False


def concatenate_videos_filter(video_paths: List[str], output_path: str, 
                               trace_callback=None) -> bool:
    """
    Concatenate videos using filter_complex for proper audio handling.
    All input videos must have same resolution and audio format.
    """
    def log(msg):
        if trace_callback:
            trace_callback(msg)
        print(msg)
    
    n = len(video_paths)
    if n == 0:
        return False
    
    if n == 1:
        import shutil
        shutil.copy(video_paths[0], output_path)
        return True
    
    # Build filter_complex string for concat
    # Input streams: [0:v][0:a][1:v][1:a]...
    filter_inputs = "".join([f"[{i}:v][{i}:a]" for i in range(n)])
    filter_str = f"{filter_inputs}concat=n={n}:v=1:a=1[outv][outa]"
    
    # Build input arguments
    input_args = []
    for vpath in video_paths:
        input_args.extend(["-i", vpath])
    
    cmd = [
        "ffmpeg", "-y",
        *input_args,
        "-filter_complex", filter_str,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-loglevel", "warning",
        output_path
    ]
    
    log(f"  🔗 Concatenating {n} videos with filter_complex...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and Path(output_path).exists():
        out_dur = get_media_duration(output_path)
        has_audio = has_audio_track(output_path)
        log(f"  ✅ Concatenated: {out_dur:.1f}s, has_audio={has_audio}")
        return True
    else:
        log(f"  ❌ Concat failed: {result.stderr[:300]}")
        return False


def merge_video_segments(segments: List[Dict], output_path: str = None,
                        session_dir: Path = None, trace_callback=None) -> Optional[str]:
    """
    Merge multiple video segments into one final video.
    
    NEW APPROACH:
    1. Each segment with audio → merged with audio baked in
    2. Each segment without audio → add silent audio track
    3. All segments → concatenate using filter_complex
    
    Args:
        segments: List of dicts with keys:
            - segment_id: identifier
            - video_path: path to video file
            - audio_path: optional path to audio file
        output_path: Where to save final video (auto-generated if None)
        session_dir: Session directory for temp files
        trace_callback: Optional callback for logging
        
    Returns:
        Path to final video or None on failure
    """
    def log(msg):
        if trace_callback:
            trace_callback(msg)
        print(msg)
    
    if not segments:
        log("❌ No segments to merge")
        return None
    
    if not check_ffmpeg():
        log("❌ FFmpeg not found - please install ffmpeg")
        return None
    
    # Determine output path
    if output_path is None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        out_dir = session_dir if session_dir else OUTPUT_DIR
        output_path = str(out_dir / f"final_video_{timestamp}.mp4")
    
    # Temp directory for intermediate files
    temp_dir = (session_dir / "temp") if session_dir else TEMP_DIR
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    log(f"\n🎬 Merging {len(segments)} segments...")
    
    # STEP 1: Process each segment - create merged videos with audio
    prepared_videos = []
    
    for i, seg in enumerate(segments):
        seg_id = seg.get("segment_id", f"seg_{i}")
        video_path = seg.get("video_path")
        audio_path = seg.get("audio_path")
        
        if not video_path or not Path(video_path).exists():
            log(f"  ⚠️ Segment {seg_id}: video not found, skipping")
            continue
        
        prepared_path = str(temp_dir / f"prepared_{i}_{seg_id}.mp4")
        
        if audio_path and Path(audio_path).exists():
            # Merge video with audio
            log(f"  🔊 Segment {seg_id}: merging video + audio...")
            if create_segment_with_audio(video_path, audio_path, prepared_path, trace_callback):
                prepared_videos.append(prepared_path)
            else:
                log(f"  ⚠️ Segment {seg_id}: merge failed, trying silent")
                if create_silent_video(video_path, prepared_path, trace_callback):
                    prepared_videos.append(prepared_path)
        else:
            # No audio - add silent track
            log(f"  🔇 Segment {seg_id}: no audio, adding silent track...")
            if create_silent_video(video_path, prepared_path, trace_callback):
                prepared_videos.append(prepared_path)
    
    if not prepared_videos:
        log("❌ No valid videos after preparation")
        return None
    
    # STEP 2: Verify all prepared videos have audio
    log(f"\n  📋 Verifying {len(prepared_videos)} prepared videos...")
    for i, vpath in enumerate(prepared_videos):
        dur = get_media_duration(vpath)
        has_aud = has_audio_track(vpath)
        log(f"    [{i}] {Path(vpath).name}: {dur:.1f}s, audio={has_aud}")
    
    # STEP 3: Concatenate all videos
    log(f"\n  🔗 Final concatenation...")
    if concatenate_videos_filter(prepared_videos, output_path, trace_callback):
        duration = get_media_duration(output_path)
        has_audio = has_audio_track(output_path)
        log(f"\n✅ Final video: {output_path}")
        log(f"   Duration: {duration:.1f}s, Has Audio: {has_audio}")
        return output_path
    else:
        log("❌ Final concatenation failed")
        return None


# Keep old function for backward compatibility
def add_audio_to_video(video_path: str, audio_path: str, output_path: str, 
                       trace_callback=None) -> bool:
    """Legacy wrapper - use create_segment_with_audio instead."""
    return create_segment_with_audio(video_path, audio_path, output_path, trace_callback)


if __name__ == "__main__":
    # Test
    print("FFmpeg available:", check_ffmpeg())
