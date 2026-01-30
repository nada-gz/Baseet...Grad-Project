"""
Streamlit Demo for Educational Video Generator
Simple UI with prompt input, tracing, and video output
"""
import streamlit as st
import asyncio
import time
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Educational Video Generator",
    page_icon="🎬",
    layout="wide"
)

# Import pipeline (after streamlit config)
from pipeline_v2 import EducationalVideoPipeline


def init_session_state():
    """Initialize session state variables."""
    if "logs" not in st.session_state:
        st.session_state.logs = []
    if "generating" not in st.session_state:
        st.session_state.generating = False
    if "video_path" not in st.session_state:
        st.session_state.video_path = None
    if "session_dir" not in st.session_state:
        st.session_state.session_dir = None


def add_log(msg: str):
    """Add log message to session state."""
    st.session_state.logs.append(msg)


async def run_pipeline(topic: str, duration: float, log_container, status_text, progress_bar):
    """Run the video generation pipeline with live updates."""
    
    logs = []
    
    def trace_callback(msg: str):
        logs.append(msg)
        # Update the log display
        log_container.code("\n".join(logs[-30:]), language=None)
    
    pipeline = EducationalVideoPipeline(
        trace_callback=trace_callback,
        target_duration_minutes=duration
    )
    
    status_text.text("🚀 Starting pipeline...")
    progress_bar.progress(10)
    
    result = await pipeline.generate(topic)
    
    progress_bar.progress(100)
    
    return result, logs


def main():
    init_session_state()
    
    # Header
    st.title("🎬 Educational Video Generator")
    st.markdown("""
    Generate educational videos with **English visuals** and **Arabic narration**.
    Simply enter a topic and watch the AI create an educational video!
    """)
    
    st.divider()
    
    # Two-column layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Input")
        
        # Topic input
        topic = st.text_input(
            "Educational Topic",
            placeholder="e.g., Newton's Laws of Motion, DNA Structure, Photosynthesis...",
            help="Enter any educational topic you want to create a video about"
        )
        
        # Duration slider
        duration = st.slider(
            "Target Duration (minutes)",
            min_value=0.5,
            max_value=3.0,
            value=1.0,
            step=0.5,
            help="Longer videos will have more segments"
        )
        
        # Example topics
        st.markdown("**Quick examples:**")
        example_cols = st.columns(3)
        
        examples = [
            "Newton's Laws of Motion",
            "Cell Division",
            "Water Cycle"
        ]
        
        for i, ex in enumerate(examples):
            with example_cols[i]:
                if st.button(ex, key=f"ex_{i}", use_container_width=True):
                    st.session_state.selected_topic = ex
                    st.rerun()
        
        # Use selected example if available
        if hasattr(st.session_state, 'selected_topic') and st.session_state.selected_topic:
            topic = st.session_state.selected_topic
            st.session_state.selected_topic = None
        
        st.divider()
        
        # Generate button
        if st.button("🎬 Generate Video", type="primary", use_container_width=True, 
                    disabled=not topic or st.session_state.generating):
            
            st.session_state.generating = True
            st.session_state.logs = []
            st.session_state.video_path = None
            
            # Progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Run pipeline
            with st.spinner("Generating video..."):
                result, logs = asyncio.run(
                    run_pipeline(topic, duration, st.empty(), status_text, progress_bar)
                )
            
            st.session_state.generating = False
            st.session_state.logs = logs
            
            if result["success"]:
                st.session_state.video_path = result["video_path"]
                st.session_state.session_dir = result["session_dir"]
                st.success("✅ Video generated successfully!")
            else:
                st.error(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
            
            st.rerun()
    
    with col2:
        st.subheader("🎥 Output")
        
        # Video display
        if st.session_state.video_path and Path(st.session_state.video_path).exists():
            st.video(st.session_state.video_path)
            
            # Download button
            with open(st.session_state.video_path, "rb") as f:
                st.download_button(
                    label="📥 Download Video",
                    data=f,
                    file_name=f"educational_video.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )
            
            # Session info
            if st.session_state.session_dir:
                st.caption(f"📁 Output folder: `{st.session_state.session_dir}`")
        else:
            st.info("🎬 Your generated video will appear here")
    
    st.divider()
    
    # Logs section (full width)
    st.subheader("📋 Pipeline Trace")
    
    if st.session_state.logs:
        # Show logs in expandable section
        with st.expander("View detailed logs", expanded=True):
            log_text = "\n".join(st.session_state.logs)
            st.code(log_text, language=None)
    else:
        st.info("Pipeline logs will appear here during generation")
    
    # Footer
    st.divider()
    st.caption("Built with Manim, Qwen, and ElevenLabs | English visuals + Arabic narration")


if __name__ == "__main__":
    main()
