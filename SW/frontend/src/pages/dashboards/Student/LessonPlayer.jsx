import { useParams } from "react-router-dom";
import { Play, Pause, Mic, Send, HelpCircle } from "lucide-react";

export default function LessonPlayer() {
  const { lessonId } = useParams();

  return (
    <div className="lesson-player">
      {/* Center Floating Asset */}
      <img
        src={require("../../../assets/cute_baseet.png")}
        alt="cute Baseet"
        className="floating-asset center-between"
      />

      {/* Right Side Floating Asset */}
      <img
        src={require("../../../assets/crazy_baseet.png")}
        alt="falling Baseet"
        className="floating-asset right-side"
      />

      {/* Header */}
      <div className="lesson-player-header">
        <h1>Lesson {lessonId}</h1>

        <div className="lesson-helper">
          <img
            src={require("../../../assets/BASEET-smiling.png")}
            alt="Baseet helper"
          />
          <span>Hi! I’m Baseet 👋</span>
        </div>
      </div>

      {/* Video Section */}
      <div className="lesson-video" style={{ position: "relative" }}>
        <div className="video-placeholder">
          🎥 Lesson Video Here
        </div>

        <img
          src={require("../../../assets/eyes_baseet.png")}
          alt="Eyes on border"
          className="eyes-border"
        />
      </div>




      {/* Controls */}
      <div className="lesson-controls">
        <button className="lesson-btn primary">
          <Play size={22} /> Play
        </button>

        <button className="lesson-btn secondary">
          <Pause size={22} /> Pause
        </button>

        <button className="lesson-btn outline">
          <Mic size={22} /> Record
        </button>
      </div>

      {/* Q&A Section */}
      <div className="lesson-qa">
        <div className="qa-header">
          <HelpCircle size={22} />
          <span>Ask Baseet</span>
        </div>

        <textarea
          placeholder="Type your question here ✨"
        />

        <button className="lesson-btn primary send-btn">
          <Send size={18} /> Send
        </button>
      </div>
    </div>
  );
}
