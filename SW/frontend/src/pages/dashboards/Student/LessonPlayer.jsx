import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import api from "../../../services/api";
import useAuth from "../../../hooks/useAuth"; // <-- added
import { Play, Pause, Mic, Send, HelpCircle } from "lucide-react";

export default function LessonPlayer() {
  const { lessonId } = useParams();
  const { user: student, loading: authLoading } = useAuth(); // <-- get logged-in student
  const [lesson, setLesson] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadLesson = async () => {
      if (!student) return; // wait until student info is loaded

      try {
        // Call backend to get a single lesson for this student
        const res = await api.get(`/students/${student.id}/lessons/${lessonId}`);
        console.log("Lesson loaded:", res.data);
        setLesson(res.data);
      } catch (error) {
        console.error("Failed to load lesson:", error);
        setLesson(null);
      } finally {
        setLoading(false);
      }
    };

    loadLesson();
  }, [lessonId, student]);

  if (authLoading || loading) return <div>Loading lesson...</div>;
  if (!lesson) return <div>Lesson not found.</div>;

  return (
    <div className="lesson-player">
      {/* Center Floating Asset */}
      {/* <img
        src={require("../../../assets/cute_baseet.png")}
        alt="cute Baseet"
        className="floating-asset center-between"
      /> */}

      {/* Right Side Floating Asset */}
      <img
        src={require("../../../assets/crazy_baseet.png")}
        alt="falling Baseet"
        className="floating-asset right-side"
      />

      {/* ================= HEADER ================= */}
      <div className="lesson-player-header">
        <h1>
          <span className="lesson-number">{lesson.number}</span>{" "}
          {lesson.title}
        </h1>

        <div className="lesson-helper">
          <img
            src={require("../../../assets/BASEET-smiling.png")}
            alt="Baseet helper"
          />
          <span>Hi! I’m Baseet 👋</span>
        </div>
      </div>

      {/* ================= VIDEO ================= */}
      <div className="lesson-video" style={{ position: "relative" }}>
        <div className="video-placeholder">🎥 Lesson Video Here</div>

        <img
          src={require("../../../assets/eyes_baseet.png")}
          alt="Eyes on border"
          className="eyes-border"
        />
      </div>

      {/* ================= CONTROLS ================= */}
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

      {/* ================= Q&A ================= */}
      <div className="lesson-qa">
        <div className="qa-header">
          <HelpCircle size={22} />
          <span>Ask Baseet</span>
        </div>

        <textarea placeholder="Type your question here ✨" />

        <button className="lesson-btn primary send-btn">
          <Send size={18} /> Send
        </button>
      </div>
    </div>
  );
}
